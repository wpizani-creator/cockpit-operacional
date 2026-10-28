/**
 * ================================================================================================
 * ARQUIVO: setup.js (Gerenciamento de Setups Operacionais)
 * ATUALIZADO EM: 2026-09-01
 * CONTEXTO / REGRAS DE NEGÓCIO:
 * - Gerenciamento, adição, edição inline, exclusão e persistência via LocalStorage ('cockpit_setups') 
 *   dos setups operacionais de day trade (como Setup Diamante, 15 min, estratégias de índice/dólar).
 * ================================================================================================
 */

let listaSetups = JSON.parse(localStorage.getItem('cockpit_setups')) || [
    { id: 1, nome: "3º Candle 1M", stop: "150", alvo: "300", obs: "Aguardar fechamento do 3º candle." },
    { id: 2, nome: "Ativos Bolsa", stop: "200", alvo: "400", obs: "Monitorar volatilidade inicial." }
];

function salvarStorageSetups() {
    localStorage.setItem('cockpit_setups', JSON.stringify(listaSetups));
}

function inicializarSetups() {
    renderizarTabelaSetups();
}

function renderizarTabelaSetups() {
    const corpo = document.getElementById('tabela-setups-corpo');
    if (!corpo) return;

    corpo.innerHTML = listaSetups.map((item, index) => `
        <tr class="hover:bg-[#161b22]/50 transition">
            <td class="p-3"><input type="text" value="${item.nome}" onchange="atualizarSetup(${index}, 'nome', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3"><input type="number" value="${item.stop}" onchange="atualizarSetup(${index}, 'stop', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3"><input type="number" value="${item.alvo}" onchange="atualizarSetup(${index}, 'alvo', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3"><input type="text" value="${item.obs}" onchange="atualizarSetup(${index}, 'obs', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3 text-center"><button onclick="excluirSetup(${index}, '${item.nome}')" class="bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white px-2.5 py-1 rounded text-xs transition cursor-pointer">Excluir</button></td>
        </tr>
    `).join('');
}

function adicionarSetup() {
    listaSetups.unshift({ id: Date.now(), nome: "Novo Setup", stop: "150", alvo: "300", obs: "Descrever regras..." });
    salvarStorageSetups();
    renderizarTabelaSetups();
    document.getElementById('feedback-tabela').innerText = "Novo setup adicionado e salvo!";
}

function atualizarSetup(index, campo, valor) {
    listaSetups[index][campo] = valor;
    salvarStorageSetups();
    document.getElementById('feedback-tabela').innerText = `Alterações salvas para: ${listaSetups[index].nome}`;
}

function excluirSetup(index, nomeSetup) {
    if (confirm(`Deseja excluir o setup "${nomeSetup}"?`)) {
        listaSetups.splice(index, 1);
        salvarStorageSetups();
        renderizarTabelaSetups();
        document.getElementById('feedback-tabela').innerText = `Setup "${nomeSetup}" excluído e salvo.`;
    }
}