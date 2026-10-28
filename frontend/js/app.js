// ================================================================================================
// ARQUIVO: frontend/js/app.js
// CONTEXTO: Roteador Principal e Gerenciador de Módulos do Cockpit Operacional
// ================================================================================================

function carregarModulo(titulo, descricao, tipo) {
    const container = document.getElementById('conteudo-modulo');
    if (!container) return;

    if (tipo === 'trades') {
        container.innerHTML = `
            <div class="max-w-7xl mx-auto space-y-6">
                <!-- Cabeçalho do Módulo & Estatísticas -->
                <div class="flex justify-between items-center bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg">
                    <div>
                        <h2 class="text-xl font-bold text-white flex items-center gap-2">
                            <span>📊 Importação & Extrato do Profit</span>
                        </h2>
                        <p class="text-sm text-gray-400 mt-1">Visualização consolidada das ordens importadas via arquivo CSV.</p>
                    </div>
                    <div class="flex items-center gap-3">
                        <span id="totalRegistros" class="text-xs px-3 py-1.5 bg-blue-950 text-blue-400 rounded-lg border border-blue-800 font-medium">0 registros</span>
                    </div>
                </div>

                <!-- Área de Drop/Upload do CSV -->
                <div ondragover="event.preventDefault()" ondrop="tratarDropArquivo(event)" class="border-2 border-dashed border-gray-700 hover:border-blue-500 bg-gray-900/40 rounded-xl p-6 text-center transition cursor-pointer relative group">
                    <input type="file" id="fileInput" onchange="processarArquivoManual(this)" class="absolute inset-0 opacity-0 cursor-pointer w-full h-full" accept=".csv">
                    <div class="space-y-2 pointer-events-none">
                        <div class="text-2xl text-blue-400"><i class="fa-solid fa-cloud-arrow-up"></i></div>
                        <h3 class="text-sm font-semibold text-gray-200">Arraste seu <span class="text-blue-400">trade.csv</span> aqui ou clique para buscar</h3>
                        <p class="text-xs text-gray-500">Compatível com o formato padrão de exportação do ProfitChart</p>
                    </div>
                </div>

                <!-- Tabela de Trades -->
                <div class="bg-gray-900 border border-gray-800 rounded-xl shadow-xl overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-gray-300 border-collapse">
                            <thead class="bg-gray-950 text-gray-400 uppercase font-semibold border-b border-gray-800">
                                <tr>
                                    <th class="p-3">#</th>
                                    <th class="p-3">Data/Hora</th>
                                    <th class="p-3">Ativo</th>
                                    <th class="p-3">Conta</th>
                                    <th class="p-3">Lado</th>
                                    <th class="p-3">Qtd</th>
                                    <th class="p-3">Preço Compra</th>
                                    <th class="p-3">Preço Venda</th>
                                    <th class="p-3">Res. Líq.</th>
                                </tr>
                            </thead>
                            <tbody id="corpoTabelaTrades" class="divide-y divide-gray-800/60">
                                <tr>
                                    <td colspan="9" class="p-8 text-center text-gray-500 italic">Nenhum trade importado.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        if (typeof inicializarTrades === 'function') {
            inicializarTrades();
        }
} else if (tipo === 'gerenciamento') {
        container.innerHTML = `
            <div class="max-w-full px-6 space-y-6">
                <!-- Cabeçalho do Módulo de Gerenciamento -->
                <div class="flex justify-between items-center bg-gray-900 border border-gray-800 p-6 rounded-xl shadow-lg">
                    <div>
                        <h2 class="text-xl font-bold text-white flex items-center gap-2">
                            <span>⚙️ Gerenciamento de Trades</span>
                        </h2>
                        <p class="text-sm text-gray-400 mt-1">Parâmetros operacionais e tratamentos avançados das operações.</p>
                    </div>
                </div>

                <!-- Tabela de Gerenciamento Ampliada (Ocupando 100% da largura) -->
                <div class="bg-gray-900 border border-gray-800 rounded-xl shadow-xl overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs text-gray-300 border-collapse whitespace-nowrap">
                            <thead class="bg-gray-950 text-gray-400 uppercase font-semibold border-b border-gray-800">
                                <tr>
                                    <th class="p-3">#</th>
                                    <th class="p-3">Data/Hora</th>
                                    <th class="p-3">Ativo</th>
                                    <th class="p-3">Conta</th>
                                    <th class="p-3">Lado</th>
                                    <th class="p-3">Res. Líq.</th>
                                    <th class="p-3">Setup</th>
                                    <th class="p-3">Entrada</th>
                                    <th class="p-3">Time Frame</th>
                                    <th class="p-3">Tipo Entrada</th>
                                    <th class="p-3">Tipo Alvo</th>
                                    <th class="p-3">Tipo Saída</th>
                                    <th class="p-3 text-center">Checklist</th>
                                    <th class="p-3">Falha Principal</th>
                                    <th class="p-3">Observações</th>
                                </tr>
                            </thead>
                            <tbody id="corpoTabelaGerenciamento" class="divide-y divide-gray-800/60">
                                <tr>
                                    <td colspan="15" class="p-8 text-center text-gray-500 italic">Nenhum dado carregado no gerenciamento.</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        if (typeof inicializarGerenciamento === 'function') {
            inicializarGerenciamento();
        }
    } else {
        container.innerHTML = `
            <div class="max-w-4xl mx-auto bg-gray-900 border border-gray-800 p-8 rounded-xl shadow-xl">
                <h2 class="text-xl font-bold text-white mb-2">${titulo}</h2>
                <p class="text-gray-400">${descricao}</p>
            </div>
        `;
    }
}