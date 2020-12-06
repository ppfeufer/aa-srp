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
            {data: 'ship'},
            {data: 'zkb_link'},
            {
                data: 'zbk_loss_amount',
                render: function(data, type, row, meta) {
                    if(type === 'display') {
                        // var currency = 'ISK';
                        // var iskValue = $.fn.dataTable.render.number(
                        //     ',',
                        //     '.'
                        // ).display(data);
                        //
                        // return iskValue + ' ' + currency;

                        return data.toLocaleString() + " ISK";
                    } else {
                        return data;
                    }
                },
                className: 'text-right'
            },
            {
                data: 'payout_amount',
                render: function(data, type, row, meta) {
                    if(type === 'display') {
                        // var currency = 'ISK';
                        // var iskValue = $.fn.dataTable.render.number(
                        //     ',',
                        //     '.'
                        // ).display(data);
                        //
                        // return iskValue + ' ' + currency;

                        return data.toLocaleString() + " ISK";
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
            {data: 'request_status'},
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [5, 8, 9]
            },
            {
                visible: false,
                targets: [10]
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
                    idx: 4,
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
            $(row).find('td:eq(7)').attr('data-params', '{csrfmiddlewaretoken:\''+  aaSrpSettings.csrfToken + '\'}');

            $(row).find('td:eq(7)').editable({
                url: aaSrpSettings.url.changeSrpAmount.replace(
                    'SRP_REQUEST_CODE',
                    data.request_code
                ),
                mode: 'inline',
                highlight: 'rgb(170,255,128)',
                placement: 'top',
                pk: data.request_code,
                type: 'number',
                title: aaSrpSettings.translation.changeSrpPayoutHeader,
                value: '',
                success: function(response, newValue) {
                    var currency = 'ISK';
                    // var iskValue = $.fn.dataTable.render.number(
                    //     ',',
                    //     '.'
                    // ).display(newValue)

                    var iskValue = newValue.toLocaleString() + " ISK";

                    $(row).find('td:eq(7)').html(iskValue);

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

    srpRequestsTable.rows().every(function() {
        var d = this.data();

        d['zbk_loss_amount'] = d['zbk_loss_amount']  + 'ISK';
        d['payout_amount'] = d['payout_amount']  + 'ISK';

        srpRequestsTable.row(this).data(d);
    });
});
