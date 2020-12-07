/* global aaSrpSettings, moment */

$(document).ready(function() {
    /**
     * Table :: SRP Requests
     */
    var srpRequestsTable = $('#tab_aasrp_srp_requests').DataTable({
        ajax: {
            url: aaSrpSettings.url.requestsForSrpLink,
            dataSrc: '',
            cache: false
        },
        columns: [
            {
                data: 'request_time',
                render: $.fn.dataTable.render.moment(
                    moment.ISO_8601,
                    aaSrpSettings.datetimeFormat
                )
            },
            {data: 'requester'},
            {data: 'character'},
            {data: 'request_code'},
            {
                data: 'ship_html',
                render: {
                    display: 'display',
                    _: 'sort'
                }
            },
            // {data: 'zkb_link'},
            {
                data: 'zbk_loss_amount',
                render: function(data, type, row, meta) {
                    if(type === 'display') {
                        return data.toLocaleString() + ' ISK';
                    } else {
                        return data;
                    }
                },
                className: 'text-right'
            },
            {
                data: 'payout_amount',
                render: function(data, type, row, meta) {
                    // console.log(type);
                    if(type === 'display') {
                        return '<span class="srp-payout-amount">' + data.toLocaleString() + ' ISK</span>';
                    } else {
                        return data;
                    }
                },
                className: 'text-right'
            },
            {
                data: 'request_status_icon',
                className: 'text-center'
            },
            {data: 'actions'},
            // hidden columns
            {data: 'ship'},
            {data: 'request_status'},
        ],
        columnDefs: [
            {
                orderable: false,
                // targets: [5, 8, 9]
                targets: [7, 8]
            },
            {
                visible: false,
                targets: [9, 10]
            },
            {
                width: 115,
                targets: [8]
            }
        ],
        order: [[0, 'asc']],
        filterDropDown: {
            columns: [
                {
                    idx: 1,
                },
                {
                    idx: 2,
                },
                {
                    idx: 9,
                    title: aaSrpSettings.translation.filterRequestShip
                },
                {
                    idx: 10,
                    title: aaSrpSettings.translation.filterRequestStatus
                }
            ],
            autoSize: false,
            bootstrap: true
        },
        paging: false,
        createdRow: function(row, data, displayIndex) {
            // Row id attr
            $(row).attr('data-row-id', displayIndex);

            // add class and data attribute to the payout cell
            $(row).find('span.srp-payout-amount').attr('data-params', '{csrfmiddlewaretoken:\''+  aaSrpSettings.csrfToken + '\'}');

            $(row).find('span.srp-payout-amount').editable({
                url: aaSrpSettings.url.changeSrpAmount.replace(
                    'SRP_REQUEST_CODE',
                    data.request_code
                ),
                // mode: 'inline',
                highlight: 'rgb(170,255,128)',
                placement: 'top',
                pk: data.request_code,
                type: 'number',
                title: aaSrpSettings.translation.changeSrpPayoutHeader,
                value: data.payout_amount,
                success: function(response, newValue) {
                    var iskValue = newValue.toLocaleString() + ' ISK';

                    // $(row).find('span.srp-payout-amount').html(iskValue);

                    srpRequestsTable.ajax.reload();
                },
                validate: function(value) {
                    if (value === null || value === '') {
                        return 'Empty values not allowed';
                    }
                }
            });
        }
    });
});
