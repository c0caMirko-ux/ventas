document.addEventListener("DOMContentLoaded", function () {
    // Variables globales
    let datosVentas = [];
    let charts = {};

    // Cargar datos iniciales
    obtenerDatos();

    // Función para obtener datos desde Flask
    function obtenerDatos() {
        fetch("/api/superstore_orders") // Asegúrate que esta ruta exista en tu backend Flask
            .then(response => response.json())
            .then(data => {
                datosVentas = data;
                poblarTabla();
                poblarFiltros();
                actualizarMetricas();
                renderizarGraficos();
            });
    }

    // Poblar tabla de datos
    function poblarTabla() {
        const tbody = document.querySelector("#tablaDatos tbody");
        tbody.innerHTML = "";

        datosVentas.forEach(item => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${item.OrderID}</td>
                <td>${item.OrderDate}</td>
                <td>${item.CustomerName}</td>
                <td>${item.Segment}</td>
                <td>${item.Country}</td>
                <td>${item.City}</td>
                <td>${item.ProductName}</td>
                <td>${item.Category}</td>
                <td>${item.Sales}</td>
                <td>${item.Quantity}</td>
                <td>${item.Profit}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Poblar opciones en los filtros dinámicos
    function poblarFiltros() {
        const campos = [
            { id: 'filterSegment', key: 'Segment' },
            { id: 'filterCountry', key: 'Country' },
            { id: 'filterCity', key: 'City' },
            { id: 'filterCategory', key: 'Category' },
            { id: 'filterSubcategory', key: 'SubCategory' },
            { id: 'filterProduct', key: 'ProductName' },
            { id: 'filterCustomer', key: 'CustomerName' },
        ];

        campos.forEach(filtro => {
            const select = document.getElementById(filtro.id);
            const valoresUnicos = [...new Set(datosVentas.map(item => item[filtro.key]))].sort();
            select.innerHTML = `<option value="">Todos</option>`;
            valoresUnicos.forEach(valor => {
                if (valor) {
                    const option = document.createElement("option");
                    option.value = valor;
                    option.text = valor;
                    select.appendChild(option);
                }
            });
        });
    }

    // Actualizar métricas principales
    function actualizarMetricas() {
        const totalSales = datosVentas.reduce((acc, curr) => acc + parseFloat(curr.Sales), 0);
        document.getElementById("totalSales").textContent = (totalSales / 1000000).toFixed(2) + "M";
    }

    // Renderizar todos los gráficos
    function renderizarGraficos() {
        crearGrafico("salesChart", "Ventas por Región", obtenerDatosPorCampo("Region", "Sales"));
        crearGrafico("profitChart", "Ganancias por Categoría", obtenerDatosPorCampo("Category", "Profit"));
        crearGrafico("subcategoryProfitChart", "Ganancias por Subcategoría", obtenerDatosPorCampo("SubCategory", "Profit"));
        crearGrafico("productProfitChart", "Ganancias por Producto", obtenerDatosPorCampo("ProductName", "Profit"));
        crearGrafico("customerProfitChart", "Ganancias por Cliente", obtenerDatosPorCampo("CustomerName", "Profit"));
        crearGrafico("orderProfitChart", "Ganancias por Orden", obtenerDatosPorCampo("OrderID", "Profit"));
        crearGrafico("segmentProfitChart", "Ganancias por Segmento", obtenerDatosPorCampo("Segment", "Profit"));
        crearGrafico("countryProfitChart", "Ganancias por País", obtenerDatosPorCampo("Country", "Profit"));
        crearGrafico("cityProfitChart", "Ganancias por Ciudad", obtenerDatosPorCampo("City", "Profit"));
        crearGrafico("regionProfitChart", "Ganancias por Región", obtenerDatosPorCampo("Region", "Profit"));
    }

    // Utilidad: agrupar datos por campo
    function obtenerDatosPorCampo(campo, valor) {
        const resumen = {};
        datosVentas.forEach(item => {
            const key = item[campo] || "Otros";
            resumen[key] = (resumen[key] || 0) + parseFloat(item[valor]);
        });

        return {
            labels: Object.keys(resumen),
            valores: Object.values(resumen)
        };
    }

    // Crear gráfico con Chart.js
    function crearGrafico(idCanvas, titulo, datos) {
        const ctx = document.getElementById(idCanvas).getContext("2d");
        if (charts[idCanvas]) charts[idCanvas].destroy();

        charts[idCanvas] = new Chart(ctx, {
            type: "bar",
            data: {
                labels: datos.labels,
                datasets: [{
                    label: titulo,
                    data: datos.valores,
                    backgroundColor: "#7E57C2"
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: titulo }
                }
            }
        });
    }

    // Listeners de filtros
    document.querySelectorAll("select").forEach(select => {
        select.addEventListener("change", () => {
            filtrarDatos();
        });
    });

    // Filtrar datos y actualizar todo
    function filtrarDatos() {
        let datosFiltrados = [...datosVentas];

        // Aplicar filtros uno a uno
        const filtros = {
            Segment: document.getElementById("filterSegment").value,
            Country: document.getElementById("filterCountry").value,
            City: document.getElementById("filterCity").value,
            Category: document.getElementById("filterCategory").value,
            SubCategory: document.getElementById("filterSubcategory").value,
            ProductName: document.getElementById("filterProduct").value,
            CustomerName: document.getElementById("filterCustomer").value,
        };

        for (let key in filtros) {
            if (filtros[key]) {
                datosFiltrados = datosFiltrados.filter(item => item[key] === filtros[key]);
            }
        }

        // Actualizar tabla, métricas y gráficos con datos filtrados
        datosVentas = datosFiltrados;
        poblarTabla();
        actualizarMetricas();
        renderizarGraficos();
    }
});
