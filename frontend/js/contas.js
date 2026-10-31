/**
 * ================================================================================================
 * ARQUIVO: frontend/js/contas.js - VERSÃO OFICIAL MIGRADA PARA FASTAPI / SQLITE
 * CONTEXTO / REGRAS DE NEGÓCIO:
 * - Gerenciamento, adição, edição inline, exclusão e persistência via API FastAPI (tabela configuracoes)
 *   das contas e taxas operacionais sincronizadas com o Módulo de Operações.
 * ================================================================================================
 */

async function salvarContasServidor(contas) {
    try {
        await fetch('/api/contas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(contas)
        });
    } catch(e) {
        console.error("Erro ao salvar contas no servidor SQLite:", e);
    }
}

// Função global chamada pelo Módulo de Operações ao importar o CSV do Profit
window.sincronizarContaAutomatica = async function(numeroConta) {
    if (!numeroConta || numeroConta.trim() === '' || numeroConta === '-') return;
    const idLimpo = numeroConta.toString().trim();
    
    try {
        const resp = await fetch('/api/contas', { credentials: 'same-origin' });
        let contas = resp.ok ? await resp.json() : [];
        if (!Array.isArray(contas)) contas = [];

        const existe = contas.some(c => c.id.toString().trim() === idLimpo);

        if (!existe) {
            contas.push({
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
            await salvarContasServidor(contas);
            // Atualiza a tabela visualmente se o usuário já estiver na aba de contas
            if (typeof window.carregarContas === 'function') {
                window.carregarContas();
            }
        }
    } catch(e) {
        console.error("Erro na sincronização automática de conta:", e);
    }
};

window.carregarContas = async function() {
    let contas = [];
    try {
        const resp = await fetch('/api/contas', { credentials: 'same-origin' });
        if (resp.ok) {
            const dados = await resp.json();
            if (Array.isArray(dados)) contas = dados;
        }
    } catch(e) {
        console.error("Erro ao carregar contas do servidor:", e);
    }

    const corpo = document.getElementById('corpoTabelaContas') || document.getElementById('tabela-contas-corpo');
    if (!corpo) return;

    if (contas.length === 0) {
        corpo.innerHTML = `
            <tr>
                <td colspan="10" class="text-center py-12 text-gray-500">
                    <i class="fa-solid fa-folder-open text-2xl mb-2 block"></i>
                    Nenhuma conta cadastrada. Importe um ficheiro CSV no módulo de Operações para registar a sua conta automaticamente.
                </td>
            </tr>`;
        return;
    }

    let htmlRows = '';
    for (let i = 0; i < contas.length; i++) {
        const c = contas[i];
        const isMesa = c.tipo === 'Mesa';
        const modeloAtual = c.modeloMeta || 'sazonal';

        htmlRows += `
            <tr class="hover:bg-gray-800/40 transition align-top">
                <td class="p-3 font-mono text-gray-400 flex items-center gap-2">
                    <i class="fa-solid fa-lock text-gray-600 text-[10px]" title="ID gerado automaticamente via importação"></i>
                    <input type="text" value="${c.id || ''}" readonly class="bg-gray-950 border border-gray-800 rounded px-2 py-1 text-gray-400 w-24 cursor-not-allowed outline-none">
                </td>
                <td class="p-3">
                    <input type="text" value="${c.corretora || ''}" onchange="atualizarConta(${i}, 'corretora', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-28 outline-none focus:border-blue-500 text-xs">
                </td>
                <td class="p-3">
                    <select onchange="atualizarConta(${i}, 'tipo', this.value); carregarContas();" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-28 outline-none focus:border-blue-500 text-xs">
                        <option value="Simulador" ${c.tipo === 'Simulador' ? 'selected' : ''}>Simulador</option>
                        <option value="Real" ${c.tipo === 'Real' ? 'selected' : ''}>Real</option>
                        <option value="Mesa" ${c.tipo === 'Mesa' ? 'selected' : ''}>Mesa Prop.</option>
                    </select>
                </td>
                <td class="p-3">
                    <select onchange="atualizarModeloConta(${i}, this.value)" class="bg-[#0d1117] border border-amber-500/50 rounded px-2 py-1 text-amber-400 w-36 outline-none focus:border-amber-500 font-semibold text-xs">
                        <option value="sazonal" ${modeloAtual === 'sazonal' ? 'selected' : ''}>Matriz Sazonal (Fixa)</option>
                        <option value="reinvestimento" ${modeloAtual === 'reinvestimento' ? 'selected' : ''}>Matriz de Reinvestimento</option>
                    </select>
                </td>
                <td class="p-3 font-mono text-xs">
                    <div class="space-y-1">
                        <div class="flex items-center gap-1 text-[10px] text-gray-400">WIN: <input type="text" value="${c.taxaWin || '0.00'}" onchange="atualizarConta(${i}, 'taxaWin', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-1.5 py-0.5 text-white w-16 outline-none focus:border-blue-500"></div>
                        <div class="flex items-center gap-1 text-[10px] text-gray-400">WDO: <input type="text" value="${c.taxaDol || '0.00'}" onchange="atualizarConta(${i}, 'taxaDol', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-1.5 py-0.5 text-white w-16 outline-none focus:border-blue-500"></div>
                    </div>
                </td>
                <td class="p-3">
                    <input type="text" value="${c.dedoDuro !== undefined ? c.dedoDuro : '1.00'}" onchange="atualizarConta(${i}, 'dedoDuro', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-20 outline-none focus:border-blue-500 font-mono text-xs" placeholder="1.00">
                </td>
                <td class="p-3">
                    <input type="text" value="${c.impostoPJ !== undefined ? c.impostoPJ : '19.00'}" onchange="atualizarConta(${i}, 'impostoPJ', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-20 outline-none focus:border-blue-500 font-mono text-xs" placeholder="19.00">
                </td>
                <td class="p-3">
                    ${isMesa ? 
                        `<input type="text" value="${c.taxaMesa || '0.00'}" onchange="atualizarConta(${i}, 'taxaMesa', this.value)" class="bg-amber-950/30 border border-amber-700/60 rounded px-2 py-1 text-amber-300 w-20 outline-none focus:border-amber-500 font-mono text-xs" placeholder="30.00">` :
                        `<span class="text-gray-600 text-[11px] italic">N/A</span>`
                    }
                </td>
                <td class="p-3">
                    <textarea onchange="atualizarConta(${i}, 'notas', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-gray-200 w-44 h-14 outline-none focus:border-blue-500 text-[11px] resize-none" placeholder="Notas...">${c.notas || ''}</textarea>
                </td>
                <td class="p-3 text-center">
                    <button onclick="excluirConta(${i})" class="text-red-400 hover:text-red-300 text-xs px-2 py-1 bg-red-950/40 border border-red-900/50 rounded transition">Excluir</button>
                </td>
            </tr>`;
    }
    corpo.innerHTML = htmlRows;
};

window.atualizarConta = async function(index, campo, valor) {
    try {
        const resp = await fetch('/api/contas', { credentials: 'same-origin' });
        let contas = resp.ok ? await resp.json() : [];
        if (contas[index]) {
            contas[index][campo] = valor;
            await salvarContasServidor(contas);
        }
    } catch(e) {}
};

window.atualizarModeloConta = async function(index, novoModelo) {
    try {
        const resp = await fetch('/api/contas', { credentials: 'same-origin' });
        let contas = resp.ok ? await resp.json() : [];
        if (contas[index]) {
            contas[index].modeloMeta = novoModelo;
            await salvarContasServidor(contas);
        }
    } catch(e) {}
};

window.excluirConta = async function(index) {
    try {
        const resp = await fetch('/api/contas', { credentials: 'same-origin' });
        let contas = resp.ok ? await resp.json() : [];
        contas.splice(index, 1);
        await salvarContasServidor(contas);
        window.carregarContas();
    } catch(e) {}
};

function inicializarContas() {
    if (typeof window.carregarContas === 'function') {
        window.carregarContas();
    }
}

if (typeof window !== 'undefined') {
    inicializarContas();
}