/* global aaSrpSettings, moment */

$(document).ready(function() {
    'use strict';

    var totalSrpAmount = 0;
    var userSrpAmount = 0;

    /**
     * Table :: SRP Links
     */
    $('#tab_aasrp_srp_links').DataTable({
        ajax: {
            url: aaSrpSettings.url.availableSrpLinks,
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
                    if(type === 'display') {
                        return data.toLocaleString() + ' ISK';
                    } else {
                        return data;
                    }
                },
                className: 'text-right srp-link-total-cost'
            },
            {data: 'srp_status'},
            {data: 'pending_requests'},
            {
                data: 'actions',
                className: 'srp-link-actions'
            }
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [10]
            },
            {
                width: 115,
                targets: [10]
            }
        ],
        order: [[2, 'asc']],
        paging: false,
        /**
         * when ever a row is created ...
         *
         * @param row
         * @param data
         * @param rowIndex
         */
        createdRow: function(row, data, rowIndex) {
            // Row id attr
            $(row).attr('data-row-id', rowIndex);

            totalSrpAmount += parseInt(data.srp_costs);
            $('.srp-dashboard-total-isk-cost-amount').html(totalSrpAmount.toLocaleString() + ' ISK');
        },
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
                    if(type === 'display') {
                        return data.toLocaleString() + ' ISK';
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
            {data: 'request_status'},
            {data: 'ship'},
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [8]
            },
            {
                visible: false,
                targets: [9, 10]
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
                    title: aaSrpSettings.translation.filterRequestShip
                },
                {
                    idx: 9,
                    title: aaSrpSettings.translation.filterRequestStatus
                }
            ],
            autoSize: false,
            bootstrap: true
        },
        /**
         * when ever a row is created ...
         *
         * @param row
         * @param data
         * @param rowIndex
         */
        createdRow: function(row, data, rowIndex) {
            // Row id attr
            $(row).attr('data-row-id', rowIndex);

            userSrpAmount += parseInt(data.payout_amount);
            $('.srp-dashboard-user-isk-cost-amount').html(userSrpAmount.toLocaleString() + ' ISK');
        },
    });
});
