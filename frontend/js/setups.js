/**
 * ================================================================================================
 * ARQUIVO: frontend/js/setups.js - VERSÃO OFICIAL MIGRADA PARA FASTAPI / SQLITE
 * CONTEXTO / REGRAS DE NEGÓCIO:
 * - Gerenciamento, adição, edição inline, exclusão e persistência via API FastAPI (tabela parametros)
 *   dos setups operacionais de day trade.
 * ================================================================================================
 */

let listaSetups = [
    { id: 1, nome: "3º Candle 1M", stop: "150", alvo: "300", obs: "Aguardar fechamento do 3º candle." },
    { id: 2, nome: "Ativos Bolsa", stop: "200", alvo: "400", obs: "Monitorar volatilidade inicial." }
];

async function carregarSetupsServidor() {
    try {
        const response = await fetch('/api/parametros?categoria=setups', { credentials: 'same-origin' });
        if (response.ok) {
            const dados = await response.json();
            if (Array.isArray(dados) && dados.length > 0) {
                // Mapeia caso venham em formato de string simples ou objetos estruturados
                listaSetups = dados.map((item, idx) => {
                    if (typeof item === 'object' && item !== null) {
                        return {
                            id: item.id || idx + 1,
                            nome: item.nome || 'Setup',
                            stop: item.stop || '150',
                            alvo: item.alvo || '300',
                            obs: item.obs || ''
                        };
                    }
                    return { id: idx + 1, nome: item, stop: '150', alvo: '300', obs: '' };
                });
            }
        }
    } catch (e) {
        console.error("Erro ao carregar setups do servidor SQLite:", e);
    }
    renderizarTabelaSetups();
}

async function salvarSetupsServidor() {
    try {
        await fetch('/api/parametros?categoria=setups', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(listaSetups)
        });
    } catch (e) {
        console.error("Erro ao salvar setups no servidor SQLite:", e);
    }
}

function inicializarSetups() {
    carregarSetupsServidor();
}

function renderizarTabelaSetups() {
    const corpo = document.getElementById('tabela-setups-corpo');
    if (!corpo) return;

    corpo.innerHTML = listaSetups.map((item, index) => `
        <tr class="hover:bg-[#161b22]/50 transition">
            <td class="p-3"><input type="text" value="${item.nome || ''}" onchange="atualizarSetup(${index}, 'nome', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3"><input type="number" value="${item.stop || ''}" onchange="atualizarSetup(${index}, 'stop', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3"><input type="number" value="${item.alvo || ''}" onchange="atualizarSetup(${index}, 'alvo', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3"><input type="text" value="${item.obs || ''}" onchange="atualizarSetup(${index}, 'obs', this.value)" class="w-full bg-[#161b22] border border-gray-700 rounded px-2 py-1 text-white text-xs focus:border-blue-500 focus:outline-none"></td>
            <td class="p-3 text-center"><button onclick="excluirSetup(${index}, '${item.nome || 'Setup'}')" class="bg-red-600/20 hover:bg-red-600 text-red-400 hover:text-white px-2.5 py-1 rounded text-xs transition cursor-pointer">Excluir</button></td>
        </tr>
    `).join('');
}

function adicionarSetup() {
    listaSetups.unshift({ id: Date.now(), nome: "Novo Setup", stop: "150", alvo: "300", obs: "Descrever regras..." });
    salvarSetupsServidor();
    renderizarTabelaSetups();
    const feedback = document.getElementById('feedback-tabela');
    if (feedback) feedback.innerText = "Novo setup adicionado e salvo no servidor!";
}

function atualizarSetup(index, campo, valor) {
    if (listaSetups[index]) {
        listaSetups[index][campo] = valor;
        salvarSetupsServidor();
        const feedback = document.getElementById('feedback-tabela');
        if (feedback) feedback.innerText = `Alterações salvas para: ${listaSetups[index].nome}`;
    }
}

function excluirSetup(index, nomeSetup) {
    if (confirm(`Deseja excluir o setup "${nomeSetup}"?`)) {
        listaSetups.splice(index, 1);
        salvarSetupsServidor();
        renderizarTabelaSetups();
        const feedback = document.getElementById('feedback-tabela');
        if (feedback) feedback.innerText = `Setup "${nomeSetup}" excluído e salvo.`;
    }
}

if (typeof window !== 'undefined') {
    inicializarSetups();
}