// ================================================================================================
// ARQUIVO: frontend/js/trades.js - VERSÃO CORRIGIDA (ALINHAMENTO EXATO DOS ÍNDICES DO CSV)
// ================================================================================================

const CHAVE_STORAGE = "trades_importados"; 
let tradesGerenciamento = [];
let linhasBrutasRaioX = [];

document.addEventListener("DOMContentLoaded", () => {
    carregarBaseTrades();
    renderizarTabelaGerenciamento();
});

function carregarBaseTrades() {
    try {
        const dados = localStorage.getItem(CHAVE_STORAGE);
        tradesGerenciamento = dados ? JSON.parse(dados) : [];
    } catch (e) {
        tradesGerenciamento = [];
    }
}

function salvarBaseTrades() {
    try {
        localStorage.setItem(CHAVE_STORAGE, JSON.stringify(tradesGerenciamento));
    } catch (e) {
        console.error("Erro ao salvar base:", e);
    }
}

function limparBaseCompleta() {
    if (confirm("Tem certeza que deseja limpar todos os registros e reiniciar a base?")) {
        localStorage.removeItem(CHAVE_STORAGE);
        localStorage.removeItem('lotes_importados');
        tradesGerenciamento = [];
        linhasBrutasRaioX = [];
        renderizarTabelaGerenciamento();
        renderizarTabelaRaioX();
        alert("Base limpa com sucesso!");
        location.reload();
    }
}

function processarArquivoManual(input) {
    const arquivo = input.files[0];
    if (!arquivo) return;

    const leitor = new FileReader();
    leitor.onload = function(e) {
        analisarEImportarTexto(e.target.result);
        input.value = ""; 
    };
    leitor.readAsText(arquivo, "ISO-8859-1");
}

function tratarDropArquivo(evento) {
    evento.preventDefault();
    if (evento.dataTransfer.files && evento.dataTransfer.files.length > 0) {
        const arquivo = evento.dataTransfer.files[0];
        const leitor = new FileReader();
        leitor.onload = function(e) {
            analisarEImportarTexto(e.target.result);
        };
        leitor.readAsText(arquivo, "ISO-8859-1");
    }
}

function analisarEImportarTexto(conteudoTexto) {
    const linhas = conteudoTexto.split(/\r?\n/).filter(l => l.trim() !== '');
    if (linhas.length === 0) return;

    linhasBrutasRaioX = [];
    let contaDetectada = "103050571";
    let indiceCabecalho = -1;

    for (let i = 0; i < Math.min(linhas.length, 5); i++) {
        const linhaAtual = linhas[i];
        if (linhaAtual.toLowerCase().includes("conta")) {
            let partes = linhaAtual.split(/[:;]/);
            if (partes.length > 1 && partes[1].trim() !== '') {
                contaDetectada = partes.slice(1).join(' ').trim().split(/[-–\s]/)[0];
            }
        } else {
            let matchConta = linhaAtual.match(/\b\d{6,12}\b/);
            if (matchConta) {
                contaDetectada = matchConta[0];
            }
        }
    }

    for (let i = 0; i < linhas.length; i++) {
        const l = linhas[i].toLowerCase();
        if (l.includes('ativo') || l.includes('abertura') || (linhas[i].match(/;/g) || []).length > 5) {
            indiceCabecalho = i;
            break;
        }
    }

    if (indiceCabecalho === -1) indiceCabecalho = 0;

    let novosTrades = 0;
    carregarBaseTrades();

    for (let i = indiceCabecalho + 1; i < linhas.length; i++) {
        const linha = linhas[i].trim();
        if (!linha) continue;

        let col = linha.split(';').map(c => c.trim());
        if (col.length < 8) continue;

        linhasBrutasRaioX.push(col);

        // ALINHAMENTO CORRIGIDO: Pula a col[0] que está vindo vazia ou com ID inútil
        let ativo = col[1] || 'WIN';
        let abertura = col[2] || '';
        let fechamento = col[3] || '';
        let tempoOp = col[4] || '';
        
        let qtdCompra = col[5] || '0';
        let qtdVenda = col[6] || '0';
        let qtdUsada = (qtdCompra !== '0' && qtdCompra !== '') ? qtdCompra : qtdVenda;

        let ladoBruto = (col[7] || 'C').toUpperCase();
        let lado = ladoBruto.includes('V') ? 'V' : 'C';

        let precoCompra = col[8] || '0,00';
        let precoVenda = col[9] || '0,00';
        
        // Define preço de entrada e saída baseado na direção da operação
        let pEntrada = lado === 'C' ? precoCompra : precoVenda;
        let pSaida = lado === 'C' ? precoVenda : precoCompra;

        // O resultado financeiro é a última ou penúltima coluna
        let idxResultado = col.length - 1;
        if (col[idxResultado] === "") idxResultado--; 
        
        let valorFormatado = (col[idxResultado] || '0').replace('R$', '').replace(/\./g, '').replace(',', '.').trim();
        let brutoNum = parseFloat(valorFormatado) || 0;

        let idUnico = `${contaDetectada}_${ativo}_${abertura}_${fechamento}_${brutoNum}`;

        const jaExiste = tradesGerenciamento.some(t => t.id === idUnico);
        if (!jaExiste) {
            tradesGerenciamento.push({
                id: idUnico,
                conta: contaDetectada,
                ativo: ativo,
                abertura: abertura,
                fechamento: fechamento,
                tempoOp: tempoOp,
                qtd: qtdUsada || '-',
                precoEntrada: pEntrada,
                precoSaida: pSaida,
                total: brutoNum,
                lado: lado,
                setup: "",
                entrada: "",
                timeframe: "",
                tipoEntrada: "",
                tipoAlvo: "",
                tipoSaida: "",
                checklist: "",
                falha: ""
            });
            novosTrades++;
        }
    }

    salvarBaseTrades();
    renderizarTabelaGerenciamento();
    renderizarTabelaRaioX();
    alert(`Importação concluída! Novos trades adicionados: ${novosTrades}`);
}

function carregarOpcoesParametros() {
    return {
        setups: JSON.parse(localStorage.getItem('cad_setups') || '["Setup Diamante", "Cruzamento VWAP"]'),
        entradas: JSON.parse(localStorage.getItem('cad_entradas') || '["Rompimento", "Retorno"]'),
        timeframes: JSON.parse(localStorage.getItem('cad_timeframes') || '["2 min", "15 min"]'),
        tipoEntrada: JSON.parse(localStorage.getItem('cad_tipo_entrada') || '["Tendência", "Contrário"]'),
        tipoAlvo: JSON.parse(localStorage.getItem('cad_tipo_alvo') || '["Fixo", "Móvel"]'),
        tipoSaida: JSON.parse(localStorage.getItem('cad_tipo_saida') || '["Parcial", "Gain Total", "Loss"]'),
        checklist: JSON.parse(localStorage.getItem('cad_checklist') || '["Completo", "Parcial"]'),
        falhas: JSON.parse(localStorage.getItem('cad_falhas') || '["Nenhuma", "Atraso", "Saída Antecipada"]')
    };
}

function renderizarTabelaGerenciamento() {
    const corpo = document.getElementById('tabelaTradesCorpo') || document.getElementById('corpoTabelaTrades');
    const badgeTotal = document.getElementById('contadorRegistros') || document.getElementById('totalRegistros');
    const p = carregarOpcoesParametros();

    if (badgeTotal) badgeTotal.textContent = `${tradesGerenciamento.length} registros`;
    if (!corpo) return;

    if (tradesGerenciamento.length === 0) {
        corpo.innerHTML = `
            <tr>
                <td colspan="18" class="text-center py-12 text-gray-500">
                    <i class="fa-solid fa-folder-open text-2xl mb-2 block"></i>
                    Nenhuma operação importada encontrada. Faça a importação do arquivo CSV do Profit.
                </td>
            </tr>`;
        return;
    }

    corpo.innerHTML = tradesGerenciamento.map((t, index) => {
        const resultadoClass = parseFloat(t.total || 0) >= 0 ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold';
        
        const isCompra = t.lado === 'C';
        const ladoBadge = isCompra 
            ? '<span class="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-1.5 py-0.5 rounded font-bold">C</span>' 
            : '<span class="bg-red-500/20 text-red-400 border border-red-500/30 px-1.5 py-0.5 rounded font-bold">V</span>';

        return `
            <tr class="hover:bg-gray-800/40 transition border-b border-gray-800/60 text-xs">
                <td class="py-2.5 px-2 text-center font-mono text-gray-500 text-[11px]">#${index + 1}</td>
                <td class="py-2.5 px-2 font-mono text-amber-400 font-semibold whitespace-nowrap">${t.conta || '-'}</td>
                <td class="py-2.5 px-2 font-semibold text-white whitespace-nowrap">${t.ativo || '-'}</td>
                <td class="py-2.5 px-2 font-mono text-gray-300 text-[11px] whitespace-nowrap">${t.abertura || '-'}</td>
                <td class="py-2.5 px-2 font-mono text-gray-300 text-[11px] whitespace-nowrap">${t.fechamento || '-'}</td>
                <td class="py-2.5 px-2 font-mono text-gray-400 text-[11px] whitespace-nowrap">${t.tempoOp || '-'}</td>
                <td class="py-2.5 px-2 font-mono text-center text-gray-300 whitespace-nowrap">${t.qtd || '-'}</td>
                <td class="py-2.5 px-2 font-mono text-gray-300 text-[11px] whitespace-nowrap">${t.precoEntrada || '-'} / ${t.precoSaida || '-'}</td>
                <td class="py-2.5 px-2 text-center whitespace-nowrap">${ladoBadge}</td>
                <td class="py-2.5 px-2 text-right font-mono whitespace-nowrap ${resultadoClass}">
                    R$ ${parseFloat(t.total || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampo('${t.id}', 'setup', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-28">
                        <option value="">Selecione...</option>
                        ${p.setups.map(opt => `<option value="${opt}" ${t.setup === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampo('${t.id}', 'entrada', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-28">
                        <option value="">Selecione...</option>
                        ${p.entradas.map(opt => `<option value="${opt}" ${t.entrada === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampo('${t.id}', 'timeframe', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-24">
                        <option value="">Selecione...</option>
                        ${p.timeframes.map(opt => `<option value="${opt}" ${t.timeframe === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampo('${t.id}', 'tipoEntrada', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-28">
                        <option value="">Selecione...</option>
                        ${p.tipoEntrada.map(opt => `<option value="${opt}" ${t.tipoEntrada === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampo('${t.id}', 'tipoAlvo', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-24">
                        <option value="">Selecione...</option>
                        ${p.tipoAlvo.map(opt => `<option value="${opt}" ${t.tipoAlvo === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampo('${t.id}', 'tipoSaida', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-28">
                        <option value="">Selecione...</option>
                        ${p.tipoSaida.map(opt => `<option value="${opt}" ${t.tipoSaida === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampo('${t.id}', 'checklist', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-28">
                        <option value="">Selecione...</option>
                        ${p.checklist.map(opt => `<option value="${opt}" ${t.checklist === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2 flex items-center justify-between gap-1">
                    <select onchange="atualizarCampo('${t.id}', 'falha', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-24">
                        <option value="">Selecione...</option>
                        ${p.falhas.map(opt => `<option value="${opt}" ${t.falha === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                    <button onclick="remover('${t.id}')" class="text-gray-500 hover:text-red-400 p-1 cursor-pointer" title="Excluir trade">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderizarTabelaRaioX() {
    let container = document.getElementById('raioXContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'raioXContainer';
        container.className = 'mt-8 p-4 bg-gray-950 rounded-lg border border-gray-800';
        const mainContent = document.querySelector('main') || document.body;
        mainContent.appendChild(container);
    }

    if (linhasBrutasRaioX.length === 0) {
        container.innerHTML = `<h3 class="text-white font-bold mb-2">🔍 Raio-X do Arquivo Bruto:</h3><p class="text-gray-500 text-sm">Nenhum arquivo processado nesta sessão ainda.</p>`;
        return;
    }

    let linhasHtml = linhasBrutasRaioX.map(row => `
        <tr class="border-b border-gray-900 hover:bg-gray-900/40">
            ${row.map(cell => `<td class="p-2">${cell || ''}</td>`).join('')}
        </tr>
    `).join('');

    container.innerHTML = `
        <h3 class="text-white font-bold mb-2">🔍 Raio-X do Arquivo Bruto (Colunas extraídas do CSV):</h3>
        <div class="overflow-x-auto max-h-64">
            <table class="w-full text-xs text-left text-gray-300 font-mono">
                <thead class="bg-gray-900 text-gray-400 sticky top-0">
                    <tr>${linhasBrutasRaioX[0].map((_, i) => `<th class="p-2 border-b border-gray-800">[Col ${i}]</th>`).join('')}</tr>
                </thead>
                <tbody>
                    ${linhasHtml}
                </tbody>
            </table>
        </div>
    `;
}

function atualizarCampo(id, campo, val) {
    const t = tradesGerenciamento.find(x => x.id === id);
    if (t) { 
        t[campo] = val; 
        salvarBaseTrades(); 
    }
}

function remover(id) {
    tradesGerenciamento = tradesGerenciamento.filter(x => x.id !== id);
    salvarBaseTrades();
    renderizarTabelaGerenciamento();
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll('button').forEach(btn => {
        if (btn.textContent.includes("Limpar") || btn.textContent.includes("Limpar Base")) {
            btn.setAttribute("onclick", "limparBaseCompleta()");
        }
    });
});