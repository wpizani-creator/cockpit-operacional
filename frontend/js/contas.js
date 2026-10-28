/**
 * ================================================================================================
 * ARQUIVO: conta.js (Gerenciamento de Contas e Mesas Operacionais)
 * ATUALIZADO EM: 2026-09-25
 * CONTEXTO / REGRAS DE NEGÓCIO:
 * - Gerenciamento, adição, edição inline, exclusão e persistência via LocalStorage ('cockpit_contas_completo')
 *   das contas e taxas operacionais sincronizadas automaticamente com o Módulo de Operações.
 * ================================================================================================
 */

// Chave unificada oficial do sistema para contas e taxas
const STORAGE_KEY_CONTAS = 'cockpit_contas_completo';

function obterContasSalvas() {
    try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY_CONTAS) || '[]');
    } catch(e) {
        return [];
    }
}

function salvarStorageContas(contas) {
    localStorage.setItem(STORAGE_KEY_CONTAS, JSON.stringify(contas));
}

// Função global vital chamada pelo Módulo de Operações (operacoes.html) ao importar o CSV do Profit
window.sincronizarContaAutomatica = function(numeroConta) {
    if (!numeroConta || numeroConta.trim() === '' || numeroConta === '-') return;
    
    let contas = obterContasSalvas();
    const idLimpo = numeroConta.toString().trim();

    // Verifica se a conta já existe na base
    const existe = contas.some(c => c.id.toString().trim() === idLimpo);

    if (!existe) {
        // Adiciona nova conta com valores padrão abertos para edição livre
        contas.push({
            id: idLimpo,
            corretora: 'Nova Corretora',
            tipo: 'Real',
            taxaWin: '0.00',
            taxaDol: '0.00'
        });
        salvarStorageContas(contas);
    }
};

function inicializarContas() {
    renderizarTabelaContas();
}

function renderizarTabelaContas() {
    const corpo = document.getElementById('corpoTabelaContas') || document.getElementById('tabela-contas-corpo');
    if (!corpo) return;

    let contas = obterContasSalvas();

    if (contas.length === 0) {
        corpo.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-12 text-gray-500">
                    <i class="fa-solid fa-folder-open text-2xl mb-2 block"></i>
                    Nenhuma conta cadastrada. Importe um ficheiro CSV no módulo de Operações para registar a sua conta automaticamente.
                </td>
            </tr>`;
        return;
    }

    corpo.innerHTML = contas.map((c, index) => `
        <tr class="hover:bg-gray-800/40 transition">
            <td class="p-3 font-mono text-gray-400 flex items-center gap-2">
                <i class="fa-solid fa-lock text-gray-600 text-[10px]" title="ID gerado automaticamente via importação"></i>
                <input type="text" value="${c.id}" readonly class="bg-gray-950 border border-gray-800 rounded px-2 py-1 text-gray-400 w-28 cursor-not-allowed outline-none">
            </td>
            <td class="p-3">
                <input type="text" value="${c.corretora || 'Corretora'}" onchange="atualizarConta(${index}, 'corretora', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-36 outline-none focus:border-blue-500 text-xs">
            </td>
            <td class="p-3">
                <select onchange="atualizarConta(${index}, 'tipo', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-32 outline-none focus:border-blue-500 text-xs">
                    <option value="Simulador" ${c.tipo === 'Simulador' ? 'selected' : ''}>Simulador</option>
                    <option value="Real" ${c.tipo === 'Real' ? 'selected' : ''}>Real</option>
                    <option value="Mesa" ${c.tipo === 'Mesa' ? 'selected' : ''}>Mesa Proprietária</option>
                </select>
            </td>
            <td class="p-3">
                <input type="text" value="${c.taxaWin || '0.00'}" onchange="atualizarConta(${index}, 'taxaWin', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-28 outline-none focus:border-blue-500 text-xs">
            </td>
            <td class="p-3">
                <input type="text" value="${c.taxaDol || '0.00'}" onchange="atualizarConta(${index}, 'taxaDol', this.value)" class="bg-[#0d1117] border border-gray-700 rounded px-2 py-1 text-white w-28 outline-none focus:border-blue-500 text-xs">
            </td>
            <td class="p-3 text-center">
                <button onclick="excluirConta(${index})" class="text-red-400 hover:text-red-300 text-xs px-2 py-1 bg-red-950/40 border border-red-900/50 rounded transition">Excluir</button>
            </td>
        </tr>
    `).join('');
}

function atualizarConta(index, campo, valor) {
    let contas = obterContasSalvas();
    if (contas[index]) {
        contas[index][campo] = valor;
        salvarStorageContas(contas);
    }
}

function excluirConta(index) {
    let contas = obterContasSalvas();
    contas.splice(index, 1);
    salvarStorageContas(contas);
    renderizarTabelaContas();
}

// Auto-inicialização caso o script seja carregado diretamente
if (typeof window !== 'undefined') {
    inicializarContas();
}