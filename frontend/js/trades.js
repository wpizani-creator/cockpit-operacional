// ================================================================================================
// ARQUIVO: frontend/js/trades.js - VERSÃO OFICIAL PURAMENTE INTEGRADA AO FASTAPI / SQLITE
// ================================================================================================

let tradesGerenciamento = [];
let linhasBrutasRaioX = [];

document.addEventListener("DOMContentLoaded", () => {
    carregarBaseTradesServidor();
});

async function carregarBaseTradesServidor() {
    try {
        const response = await fetch('/api/trades', { credentials: 'same-origin' });
        if (response.ok) {
            const dados = await response.json();
            tradesGerenciamento = Array.isArray(dados) ? dados : [];
        } else {
            tradesGerenciamento = [];
        }
    } catch (e) {
        console.error("Erro ao carregar trades do servidor:", e);
        tradesGerenciamento = [];
    }
    renderizarTabelaGerenciamento();
}

async function salvarLoteTradesServidor(lote) {
    try {
        await fetch('/api/trades/lote', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(lote)
        });
    } catch (e) {
        console.error("Erro ao salvar lote no servidor:", e);
    }
}

async function limparBaseCompleta() {
    if (confirm("Tem certeza que deseja limpar todos os registros do servidor SQLite?")) {
        try {
            const response = await fetch('/api/trades', {
                method: 'DELETE',
                credentials: 'same-origin'
            });
            if (response.ok) {
                tradesGerenciamento = [];
                linhasBrutasRaioX = [];
                renderizarTabelaGerenciamento();
                renderizarTabelaRaioX();
                alert("Base limpa com sucesso no servidor!");
                location.reload();
            } else {
                alert("Erro ao limpar base no servidor.");
            }
        } catch (e) {
            console.error("Erro ao limpar base:", e);
        }
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

async function sincronizarContasEmLote(novasContasDetectadas) {
    if (!novasContasDetectadas || novasContasDetectadas.size === 0) return;

    try {
        const resp = await fetch('/api/contas', { credentials: 'same-origin' });
        let contasServidor = resp.ok ? await resp.json() : [];
        if (!Array.isArray(contasServidor)) contasServidor = [];

        let houveAlteracao = false;

        for (let numeroConta of novasContasDetectadas) {
            if (!numeroConta || numeroConta.trim() === '' || numeroConta === '-') continue;
            const idLimpo = numeroConta.toString().trim();

            const existe = contasServidor.some(c => c.id.toString().trim() === idLimpo);
            if (!existe) {
                contasServidor.push({
                    id: idLimpo,
                    corretora: 'Nova Corretora',
                    tipo: 'Real',
                    modeloMeta: 'sazonal',
                    taxaWin: '0.00',
                    taxaDol: '0.00',
                    dedoDuro: '1.00',
                    impostoPJ: '19.00',
                    taxaMesa: '0.00',
                    notas: 'Criada automaticamente via importação'
                });
                houveAlteracao = true;
            }
        }

        if (houveAlteracao) {
            await fetch('/api/contas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify(contasServidor)
            });
        }
    } catch(e) {
        console.error("Erro ao sincronizar contas em lote com o servidor:", e);
    }
}

async function analisarEImportarTexto(conteudoTexto) {
    const linhas = conteudoTexto.split(/\r?\n/).filter(l => l.trim() !== '');
    if (linhas.length === 0) return;

    linhasBrutasRaioX = [];
    let contasDetectadasSet = new Set();
    let contaAtualArquivo = "103050571";
    let indiceCabecalho = -1;

    for (let i = 0; i < Math.min(linhas.length, 15); i++) {
        const linhaAtual = linhas[i];
        if (linhaAtual.toLowerCase().includes("conta")) {
            let partes = linhaAtual.split(/[:;]/);
            if (partes.length > 1 && partes[1].trim() !== '') {
                let cNum = partes.slice(1).join(' ').trim().split(/[-–\s]/)[0];
                if (cNum && cNum.length >= 4 && cNum !== '-') {
                    contasDetectadasSet.add(cNum);
                    contaAtualArquivo = cNum;
                }
            }
        } else {
            let matchConta = linhaAtual.match(/\b\d{5,12}\b/);
            if (matchConta) {
                contasDetectadasSet.add(matchConta[0]);
                contaAtualArquivo = matchConta[0];
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

    let novosTradesLote = [];

    for (let i = indiceCabecalho + 1; i < linhas.length; i++) {
        const linha = linhas[i].trim();
        if (!linha) continue;

        let col = linha.split(';').map(c => c.trim());
        if (col.length < 8) continue;

        linhasBrutasRaioX.push(col);

        let contaLinha = contaAtualArquivo;
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
        
        let pEntrada = lado === 'C' ? precoCompra : precoVenda;
        let pSaida = lado === 'C' ? precoVenda : precoCompra;

        let idxResultado = col.length - 1;
        if (col[idxResultado] === "") idxResultado--; 
        
        let valorFormatado = (col[idxResultado] || '0').replace('R$', '').replace(/\./g, '').replace(',', '.').trim();
        let brutoNum = parseFloat(valorFormatado) || 0;

        let idUnico = `${contaLinha}_${ativo}_${abertura}_${fechamento}_${brutoNum}`;

        const jaExiste = tradesGerenciamento.some(t => t.id === idUnico);
        if (!jaExiste) {
            novosTradesLote.push({
                id: idUnico,
                conta: contaLinha,
                ativo: ativo,
                abertura: abertura,
                fechamento: fechamento,
                tempoOperacao: tempoOp,
                lado: lado,
                qtdCompra: qtdCompra,
                qtdVenda: qtdVenda,
                precoCompra: pEntrada,
                precoVenda: pSaida,
                resIntervaloBruto: `R$ ${brutoNum.toFixed(2)}`,
                resOperacao: `R$ ${brutoNum.toFixed(2)}`,
                setup: "",
                tipoEntrada: "",
                timeframe: "",
                checklist: "",
                falhas: ""
            });
        }
    }

    contasDetectadasSet.add(contaAtualArquivo);
    await sincronizarContasEmLote(contasDetectadasSet);

    if (novosTradesLote.length > 0) {
        await salvarLoteTradesServidor(novosTradesLote);
    }

    await carregarBaseTradesServidor();
    renderizarTabelaRaioX();
    alert(`Importação concluída! Novos trades enviados ao servidor: ${novosTradesLote.length}`);
}

function carregarOpcoesParametros() {
    return {
        setups: ["Setup Diamante", "Cruzamento VWAP"],
        entradas: ["Rompimento", "Retorno"],
        timeframes: ["2 min", "15 min"],
        tipoEntrada: ["Tendência", "Contrário"],
        tipoAlvo: ["Fixo", "Móvel"],
        tipoSaida: ["Parcial", "Gain Total", "Loss"],
        checklist: ["Completo", "Parcial"],
        falhas: ["Nenhuma", "Atraso", "Saída Antecipada"]
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
        const brutoNum = parseFloat((t.resIntervaloBruto || '0').replace('R$', '').replace(/\./g, '').replace(',', '.')) || 0;
        const resultadoClass = brutoNum >= 0 ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold';
        
        const isCompra = (t.lado || '').toUpperCase().includes('C');
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
                <td class="py-2.5 px-2 font-mono text-gray-400 text-[11px] whitespace-nowrap">${t.tempoOperacao || '-'}</td>
                <td class="py-2.5 px-2 font-mono text-center text-gray-300 whitespace-nowrap">${t.qtdCompra !== '0' && t.qtdCompra ? t.qtdCompra : (t.qtdVenda || '-')}</td>
                <td class="py-2.5 px-2 font-mono text-gray-300 text-[11px] whitespace-nowrap">${t.precoCompra || '-'} / ${t.precoVenda || '-'}</td>
                <td class="py-2.5 px-2 text-center whitespace-nowrap">${ladoBadge}</td>
                <td class="py-2.5 px-2 text-right font-mono whitespace-nowrap ${resultadoClass}">
                    R$ ${brutoNum.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampoServidor('${t.id}', 'setup', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-28">
                        <option value="">Selecione...</option>
                        ${p.setups.map(opt => `<option value="${opt}" ${t.setup === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampoServidor('${t.id}', 'tipoEntrada', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-28">
                        <option value="">Selecione...</option>
                        ${p.entradas.map(opt => `<option value="${opt}" ${t.tipoEntrada === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2">
                    <select onchange="atualizarCampoServidor('${t.id}', 'timeframe', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-24">
                        <option value="">Selecione...</option>
                        ${p.timeframes.map(opt => `<option value="${opt}" ${t.timeframe === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                </td>
                <td class="py-2.5 px-2 flex items-center justify-between gap-1">
                    <select onchange="atualizarCampoServidor('${t.id}', 'falhas', this.value)" class="bg-gray-950 border border-gray-700 text-gray-200 text-[11px] rounded px-1.5 py-1 focus:border-blue-500 focus:outline-none w-24">
                        <option value="">Selecione...</option>
                        ${p.falhas.map(opt => `<option value="${opt}" ${t.falhas === opt ? 'selected' : ''}>${opt}</option>`).join('')}
                    </select>
                    <button onclick="removerTradeServidor('${t.id}')" class="text-gray-500 hover:text-red-400 p-1 cursor-pointer" title="Excluir trade">
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

async function atualizarCampoServidor(id, campo, val) {
    const t = tradesGerenciamento.find(x => x.id === id);
    if (t) { 
        t[campo] = val; 
        await salvarLoteTradesServidor([t]); 
    }
}

async function removerTradeServidor(id) {
    if (confirm("Deseja realmente excluir este trade?")) {
        try {
            const resp = await fetch(`/api/trades/${id}`, {
                method: 'DELETE',
                credentials: 'same-origin'
            });
            if (resp.ok) {
                await carregarBaseTradesServidor();
            }
        } catch (e) {
            console.error("Erro ao excluir trade:", e);
        }
    }
}