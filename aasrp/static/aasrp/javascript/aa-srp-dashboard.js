/* global aaSrpSettings, moment */

$(document).ready(function() {
    /**
     * Table :: SRP Links
     */
    $('#tab_aasrp_srp_links').DataTable({
        ajax: {
            url: aaSrpSettings.url.activeSrpLinks,
            dataSrc: '',
            cache: false
        },
        columns: [
            {data: 'srp_name'},
            {data: 'creator'},
            {
                data: 'fleet_time',
                render: $.fn.dataTable.render.moment(
                    moment.ISO_8601,
                    aaSrpSettings.datetimeFormat
                )
            },
            {data: 'fleet_commander'},
            {data: 'fleet_doctrine'},
            {data: 'aar_link'},
            {data: 'srp_code'},
            {
                data: 'srp_costs',
                render: function(data, type, row, meta) {
                    if(type === 'display'){
                        var currency = 'ISK';
                        var iskValue = $.fn.dataTable.render.number(
                            ',',
                            '.'
                        ).display(data);

                        return iskValue + ' ' + currency;
                    } else {
                        return data;
                    }
                },
                className: 'text-right'
            },
            {data: 'srp_status'},
            {data: 'pending_requests'},
            {data: 'actions'}
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [10]
            }
        ],
        order: [[2, 'asc']],
        paging: false
    });

    /**
     * Table :: User's own SRP requests
     */
    $('#tab_aasrp_user_srp_requests').DataTable({
        ajax: {
            url: aaSrpSettings.url.userSrpRequests,
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
            {data: 'character'},
            {data: 'fleet_name'},
            {data: 'srp_code'},
            {data: 'request_code'},
            {data: 'ship'},
            {data: 'zkb_link'},
            {
                data: 'zbk_loss_amount',
                render: function(data, type, row, meta) {
                    if(type === 'display'){
                        var currency = 'ISK';
                        var iskValue = $.fn.dataTable.render.number(
                            ',',
                            '.'
                        ).display(data);

                        return iskValue + ' ' + currency;
                    } else {
                        return data;
                    }
                },
                className: 'text-right'
            },
            {
                data: 'payout_amount',
                render: function(data, type, row, meta) {
                    if(type === 'display'){
                        var currency = 'ISK';
                        var iskValue = $.fn.dataTable.render.number(
                            ',',
                            '.'
                        ).display(data);

                        return iskValue + ' ' + currency;
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
            // hidden columns
            {data: 'request_status'}
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [6, 9]
            },
            {
                visible: false,
                targets: [10]
            }
        ],
        order: [[0, 'desc']],
        filterDropDown: {
            columns: [
                {
                    idx: 1,
                },
                {
                    idx: 10,
                    title: aaSrpSettings.translation.filterRequestStatus
                }
            ],
            autoSize: false,
            bootstrap: true
        }
    });
});
