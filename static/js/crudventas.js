$(document).ready(function () {
    cargarDatos();
    cargarOpcionesFormulario();
});

function cargarDatos() {
    $('#loader').removeClass('d-none');
    $.ajax({
        url: "/api/list_orders",
        method: "GET",
        dataType: "json",
        success: function (data) {
            $('#tablaVentas').DataTable().clear().destroy();
            cargarTabla(data);
        },
        error: function (xhr, status, error) {
            console.error("Error al cargar ventas:", error);
            alert("Error al cargar ventas.");
        },
        complete: function () {
            $('#loader').addClass('d-none');
        }
    });
}

function cargarTabla(data) {
    const cuerpo = data.map(d => [
    d.id,  // <-- antes era d.RowID
    d.OrderID,
    d.OrderDate,
    d.CustomerName,
    d.City,
    d.ProductName,
    parseFloat(d.Sales).toFixed(2),
    parseInt(d.Quantity),
    parseFloat(d.Profit).toFixed(2)
]);


    $('#tablaVentas').DataTable({
        data: cuerpo,
        columns: [
            { title: "RowID", visible: false },
            { title: "OrderID" },
            { title: "Order Date" },
            { title: "Customer" },
            { title: "City" },
            { title: "Product" },
            { title: "Sales ($)", className: "text-end" },
            { title: "Quantity", className: "text-center" },
            { title: "Profit ($)", className: "text-end" },
            {
                title: "Acciones",
                orderable: false,
                searchable: false,
                className: "text-center",
                render: function (data, type, row) {
                    const id = row[0];
                    return `
                        <button class="btn btn-sm btn-warning btn-editar me-1">
                            <i class="fas fa-edit"></i> Editar
                        </button>
                        <button class="btn btn-sm btn-danger btn-eliminar" data-id="${id}">
                            <i class="fas fa-trash-alt"></i> Eliminar
                        </button>`;
                }
            }
        ],
        responsive: true
    });
}

$('#tablaVentas').on('click', '.btn-eliminar', function () {
    const id = $(this).data('id');
    if (confirm("¿Seguro que quieres eliminar este registro?")) {
        $.ajax({
            url: `/del/sales/${id}`,
            method: 'DELETE',
            success: function () {
                mostrarToast('❌ Venta eliminada', 'danger');
                cargarDatos();
            },
            error: function () {
                alert("Error al eliminar.");
            }
        });
    }
});

$('#tablaVentas').on('click', '.btn-editar', function () {
    const row = $(this).closest('tr');
    const data = $('#tablaVentas').DataTable().row(row).data();
    console.log(data);

    $('#editarRowID').val(data[0]);
    $('#editarOrderID').val(data[1]);
    $('#editarOrderDate').val(data[2]);
    $('#editarCustomerName').val(data[3]);
    $('#editarCity').val(data[4]);
    $('#editarProductName').val(data[5]);
    $('#editarSales').val(data[6]);
    $('#editarQuantity').val(data[7]);
    $('#editarProfit').val(data[8]);

    const modal = new bootstrap.Modal(document.getElementById('modalEditar'));
    modal.show();
});

$('#formEditar').on('submit', function (e) {
    e.preventDefault();
    const id = $('#editarRowID').val();
    const datos = {
        order_id: $('#editarOrderID').val(),
        order_date: $('#editarOrderDate').val(),
        customer_name: $('#editarCustomerName').val(),
        city: $('#editarCity').val(),
        product_name: $('#editarProductName').val(),
        sales: parseFloat($('#editarSales').val()),
        quantity: parseInt($('#editarQuantity').val()),
        profit: parseFloat($('#editarProfit').val())
    };

    $.ajax({
        url: `/upd/order/${id}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(datos),
        success: function () {
            $('#modalEditar').modal('hide');
            mostrarToast('✏️ Venta actualizada', 'warning');
            cargarDatos();
        },
        error: function () {
            alert('Error al actualizar');
        }
    });
});

function mostrarToast(mensaje, tipo = 'primary') {
    const toastEl = $('#toastNotificacion');
    const toastBody = $('#toastMensaje');

    toastEl.removeClass('bg-primary bg-success bg-danger bg-warning');
    toastEl.addClass(`bg-${tipo}`);
    toastBody.text(mensaje);

    const toast = new bootstrap.Toast(toastEl[0]);
    toast.show();
}

function cargarOpcionesFormulario() {
    // Si tienes combos de filtro u opciones (Segmentos, Regiones, etc.)
    $.ajax({
        url: '/api/opciones',
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            llenarCombo('#addSegment', data.segmentos);
            llenarCombo('#addRegion', data.regiones);
            // Agregar más combos si es necesario
        },
        error: function () {
            console.error("Error al cargar combos");
        }
    });
}

function llenarCombo(selector, valores) {
    const select = $(selector);
    select.empty();
    select.append('<option value="">-- Seleccione --</option>');
    valores.forEach(v => {
        select.append(`<option value="${v}">${v}</option>`);
    });
}







