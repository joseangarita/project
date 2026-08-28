import pandas as pd
import json
import os

EXCEL_FILE = 'Tramos.xlsx'
OUTPUT_HTML = 'Dashboard_Interactivo.html'

def parse_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0

def parse_str(val):
    if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
        return 'N/A'
    return str(val).strip()

def generar_dashboard():
    if not os.path.exists(EXCEL_FILE):
        print(f"Error: No se encuentra el archivo '{EXCEL_FILE}'. Asegúrate de ejecutar el script en la misma carpeta.")
        return

    print(f"Leyendo datos desde '{EXCEL_FILE}'...")
    df = pd.read_excel(EXCEL_FILE, sheet_name='Data')

    # Limpiamos espacios en blanco en columnas clave
    cols_to_clean = ['Zona', 'Ciudad', 'Nodo Origen', 'Nodo Destino', 'Nombre de enlace', 'Estado General']
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Filtrar filas sin enlace
    df = df[df['Nombre de enlace'].notnull() & (df['Nombre de enlace'] != 'nan') & (df['Nombre de enlace'] != '')]

    data_list = []
    for _, row in df.iterrows():
        distancia = parse_float(row['Distancia (mts)']) if 'Distancia (mts)' in df.columns and pd.notnull(row['Distancia (mts)']) else 0.0
        
        zona = parse_str(row['Zona']) if 'Zona' in df.columns else 'N/A'
        ciudad = parse_str(row['Ciudad']) if 'Ciudad' in df.columns else 'N/A'
        enlace = parse_str(row['Nombre de enlace']) if 'Nombre de enlace' in df.columns else 'Sin nombre'
        nodo_origen = parse_str(row['Nodo Origen']) if 'Nodo Origen' in df.columns else 'N/A'
        nodo_destino = parse_str(row['Nodo Destino']) if 'Nodo Destino' in df.columns else 'N/A'
        estado = parse_str(row['Estado General']) if 'Estado General' in df.columns else 'N/A'

        # Nuevos campos solicitados
        rx_origen = parse_str(row['RX Origen (dBm)']) if 'RX Origen (dBm)' in df.columns else 'N/A'
        crc_origen = parse_str(row['CRC/Errors Origen']) if 'CRC/Errors Origen' in df.columns else 'N/A'
        rx_destino = parse_str(row['RX Destino (dBm)']) if 'RX Destino (dBm)' in df.columns else 'N/A'
        crc_destino = parse_str(row['CRC/Errors Destino']) if 'CRC/Errors Destino' in df.columns else 'N/A'

        data_list.append({
            "zona": zona,
            "ciudad": ciudad,
            "enlace": enlace,
            "nodoOrigen": nodo_origen,
            "nodoDestino": nodo_destino,
            "distancia": distancia,
            "rxOrigen": rx_origen,
            "crcOrigen": crc_origen,
            "rxDestino": rx_destino,
            "crcDestino": crc_destino,
            "estado": estado
        })

    json_data = json.dumps(data_list, ensure_ascii=False)

    html_content = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Monitoreo de Tramos</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen p-6 font-sans">

    <!-- Header -->
    <header class="mb-8 border-b border-slate-800 pb-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
            <h1 class="text-3xl font-bold text-sky-400 flex items-center gap-3">
                <i data-lucide="activity"></i> Dashboard Monitoreo de Tramos
            </h1>
            <p class="text-slate-400 text-sm mt-1">Sincronizado dinámicamente desde Tramos.xlsx</p>
        </div>
        <button onclick="resetFilters()" class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold rounded-lg border border-slate-700 flex items-center gap-2 transition-all">
            <i data-lucide="rotate-ccw" class="w-4 h-4"></i> Limpiar Filtros
        </button>
    </header>

    <!-- Filtros -->
    <section class="bg-slate-800/60 border border-slate-700/60 p-5 rounded-xl mb-8 shadow-xl backdrop-blur-sm">
        <h2 class="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
            <i data-lucide="filter" class="w-4 h-4 text-sky-400"></i> Buscadores Libres
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
                <label for="filterZona" class="block text-xs font-semibold text-slate-300 uppercase mb-2">Zona</label>
                <input type="text" id="filterZona" onkeyup="applyFilters()" placeholder="Buscar zona..." class="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 focus:outline-none placeholder-slate-500">
            </div>
            <div>
                <label for="filterCiudad" class="block text-xs font-semibold text-slate-300 uppercase mb-2">Ciudad</label>
                <input type="text" id="filterCiudad" onkeyup="applyFilters()" placeholder="Buscar ciudad..." class="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 focus:outline-none placeholder-slate-500">
            </div>
            <div>
                <label for="filterNodoSelect" class="block text-xs font-semibold text-slate-300 uppercase mb-2">Nodo (Origen/Destino)</label>
                <input type="text" id="filterNodoSelect" onkeyup="applyFilters()" placeholder="Buscar nodo..." class="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 focus:outline-none placeholder-slate-500">
            </div>
            <div>
                <label for="filterTramo" class="block text-xs font-semibold text-slate-300 uppercase mb-2">Nombre de Enlace / Tramo</label>
                <input type="text" id="filterTramo" onkeyup="applyFilters()" placeholder="Buscar por tramo..." class="w-full bg-slate-900 border border-slate-700 text-slate-200 rounded-lg p-2.5 focus:ring-2 focus:ring-sky-500 focus:outline-none placeholder-slate-500">
            </div>
        </div>
    </section>

    <!-- Tarjetas KPI -->
    <section class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div class="bg-slate-800/80 border border-slate-700 p-5 rounded-xl shadow-lg flex items-center justify-between">
            <div>
                <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Total Enlaces</p>
                <h3 id="kpiTotal" class="text-3xl font-extrabold text-white mt-1">0</h3>
            </div>
            <div class="p-3 bg-sky-500/10 text-sky-400 rounded-lg border border-sky-500/20">
                <i data-lucide="layers" class="w-6 h-6"></i>
            </div>
        </div>
        <div class="bg-slate-800/80 border border-slate-700 p-5 rounded-xl shadow-lg flex items-center justify-between">
            <div>
                <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Estado OK</p>
                <h3 id="kpiOK" class="text-3xl font-extrabold text-emerald-400 mt-1">0</h3>
            </div>
            <div class="p-3 bg-emerald-500/10 text-emerald-400 rounded-lg border border-emerald-500/20">
                <i data-lucide="check-circle-2" class="w-6 h-6"></i>
            </div>
        </div>
        <div class="bg-slate-800/80 border border-slate-700 p-5 rounded-xl shadow-lg flex items-center justify-between">
            <div>
                <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Requieren Revisión</p>
                <h3 id="kpiRevisar" class="text-3xl font-extrabold text-rose-400 mt-1">0</h3>
            </div>
            <div class="p-3 bg-rose-500/10 text-rose-400 rounded-lg border border-rose-500/20">
                <i data-lucide="alert-triangle" class="w-6 h-6"></i>
            </div>
        </div>
        <div class="bg-slate-800/80 border border-slate-700 p-5 rounded-xl shadow-lg flex items-center justify-between">
            <div>
                <p class="text-slate-400 text-xs font-bold uppercase tracking-wider">Distancia Total Red</p>
                <h3 id="kpiDistancia" class="text-3xl font-extrabold text-indigo-400 mt-1">0 Km</h3>
            </div>
            <div class="p-3 bg-indigo-500/10 text-indigo-400 rounded-lg border border-indigo-500/20">
                <i data-lucide="ruler" class="w-6 h-6"></i>
            </div>
        </div>
    </section>

    <!-- Tabla -->
    <section class="bg-slate-800/50 border border-slate-700/80 rounded-xl shadow-2xl overflow-hidden">
        <div class="p-4 border-b border-slate-700/80 flex justify-between items-center">
            <h2 class="font-bold text-slate-200 flex items-center gap-2">
                <i data-lucide="list" class="w-5 h-5 text-sky-400"></i> Registros de Tramos
            </h2>
            <span id="counterRows" class="text-xs bg-slate-700 text-slate-300 px-3 py-1 rounded-full font-mono">0 Registros</span>
        </div>
        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse text-sm">
                <thead>
                    <tr class="bg-slate-900/80 text-slate-400 uppercase text-xs font-semibold tracking-wider border-b border-slate-700">
                        <th class="p-4">Zona</th>
                        <th class="p-4">Ciudad</th>
                        <th class="p-4">Nombre de Enlace</th>
                        <th class="p-4">RX Origen (dBm)</th>
                        <th class="p-4">CRC/Errors Origen</th>
                        <th class="p-4">RX Destino (dBm)</th>
                        <th class="p-4">CRC/Errors Destino</th>
                        <th class="p-4 text-center">Estado General</th>
                    </tr>
                </thead>
                <tbody id="tableBody" class="divide-y divide-slate-700/50 text-slate-300">
                </tbody>
            </table>
        </div>
    </section>

    <script>
        const rawData = """ + json_data + """;

        document.addEventListener("DOMContentLoaded", () => {
            applyFilters();
            lucide.createIcons();
        });

        function applyFilters() {
            const searchZona = document.getElementById("filterZona").value.toLowerCase().trim();
            const searchCiudad = document.getElementById("filterCiudad").value.toLowerCase().trim();
            const searchNodo = document.getElementById("filterNodoSelect").value.toLowerCase().trim();
            const searchTramo = document.getElementById("filterTramo").value.toLowerCase().trim();

            const filteredData = rawData.filter(item => {
                const matchZona = searchZona === "" || (item.zona && item.zona.toLowerCase().includes(searchZona));
                const matchCiudad = searchCiudad === "" || (item.ciudad && item.ciudad.toLowerCase().includes(searchCiudad));
                
                // La búsqueda por nodo sigue funcionando buscando en las propiedades nodoOrigen y nodoDestino 
                // aunque no estén visibles en la tabla.
                const nodoO = item.nodoOrigen ? item.nodoOrigen.toLowerCase() : "";
                const nodoD = item.nodoDestino ? item.nodoDestino.toLowerCase() : "";
                const matchNodo = searchNodo === "" || nodoO.includes(searchNodo) || nodoD.includes(searchNodo);
                
                const matchTramo = searchTramo === "" || (item.enlace && item.enlace.toLowerCase().includes(searchTramo));
                
                return matchZona && matchCiudad && matchNodo && matchTramo;
            });

            updateKPIs(filteredData);
            renderTable(filteredData);
        }

        function updateKPIs(data) {
            const total = data.length;
            const okCount = data.filter(d => d.estado === "OK").length;
            const revisarCount = data.filter(d => d.estado === "REVISAR").length;
            
            // Calculamos la distancia para el KPI usando la propiedad oculta item.distancia
            const totalMts = data.reduce((acc, curr) => acc + curr.distancia, 0);
            const totalKm = (totalMts / 1000).toLocaleString('es-CO', { minimumFractionDigits: 1, maximumFractionDigits: 1 });

            document.getElementById("kpiTotal").textContent = total;
            document.getElementById("kpiOK").textContent = okCount;
            document.getElementById("kpiRevisar").textContent = revisarCount;
            document.getElementById("kpiDistancia").textContent = `${totalKm} Km`;
            document.getElementById("counterRows").textContent = `${total} Registros`;
        }

        function renderTable(data) {
            const tbody = document.getElementById("tableBody");
            tbody.innerHTML = "";

            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="p-6 text-center text-slate-500">No se encontraron tramos.</td></tr>`;
                return;
            }

            data.forEach(item => {
                const isOK = item.estado === "OK";
                const badgeClass = isOK 
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30" 
                    : "bg-rose-500/10 text-rose-400 border-rose-500/30 animate-pulse";
                const badgeIcon = isOK ? "check" : "alert-circle";

                const row = document.createElement("tr");
                row.className = "hover:bg-slate-800/60 transition-colors";
                row.innerHTML = `
                    <td class="p-4 text-xs text-slate-400 font-semibold">${item.zona}</td>
                    <td class="p-4 font-semibold text-slate-200">${item.ciudad}</td>
                    <td class="p-4 font-mono text-xs text-sky-300">${item.enlace}</td>
                    <td class="p-4 font-mono">${item.rxOrigen}</td>
                    <td class="p-4 font-mono">${item.crcOrigen}</td>
                    <td class="p-4 font-mono">${item.rxDestino}</td>
                    <td class="p-4 font-mono">${item.crcDestino}</td>
                    <td class="p-4 text-center">
                        <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${badgeClass}">
                            <i data-lucide="${badgeIcon}" class="w-3.5 h-3.5"></i>
                            ${item.estado}
                        </span>
                    </td>
                `;
                tbody.appendChild(row);
            });

            lucide.createIcons();
        }

        function resetFilters() {
            document.getElementById("filterZona").value = "";
            document.getElementById("filterCiudad").value = "";
            document.getElementById("filterNodoSelect").value = "";
            document.getElementById("filterTramo").value = "";
            applyFilters();
        }
    </script>
</body>
</html>"""

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"¡Éxito! Dashboard actualizado con {len(data_list)} registros en '{OUTPUT_HTML}'.")

if __name__ == '__main__':
    generar_dashboard()
