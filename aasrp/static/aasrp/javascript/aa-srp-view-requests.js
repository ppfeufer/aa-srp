/* global aaSrpSettings, moment */

$(document).ready(function() {
    'use strict';

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
                /**
                 * render callback
                 *
                 * @param data
                 * @param type
                 * @param row
                 * @param meta
                 * @returns {string|*}
                 */
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
                /**
                 * render callback
                 *
                 * @param data
                 * @param type
                 * @param row
                 * @param meta
                 * @returns {string|*}
                 */
                render: function(data, type, row, meta) {
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
            {
                data: 'actions',
                className: 'srp-request-actions'
            },

            /**
             * hidden columns
             */
            {data: 'ship'},
            {data: 'request_status'},
        ],
        columnDefs: [
            {
                orderable: false,
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

            // add class and data attribute to the payout span
            $(row).find('span.srp-payout-amount').addClass('srp-request-' + data.request_code);
            $(row).find('span.srp-payout-amount').attr('data-params', '{csrfmiddlewaretoken:\''+  aaSrpSettings.csrfToken + '\'}');
            $(row).find('span.srp-payout-amount').attr('data-pk', data.request_code);
            $(row).find('span.srp-payout-amount').attr('data-value', data.payout_amount);
            $(row).find('span.srp-payout-amount').attr('data-url', aaSrpSettings.url.changeSrpAmount.replace(
                'SRP_REQUEST_CODE',
                data.request_code
            ));
        },
    });

    /**
     * make srp payout field editable
     */
    $('#tab_aasrp_srp_requests').editable({
        container: 'body',
        selector: '.srp-payout-amount',
        title: aaSrpSettings.translation.changeSrpPayoutHeader,
        type: 'number',
        placement: 'top',
        /**
         * @param value
         * @param response
         * @returns {boolean}
         */
        display: function(value, response) {
            return false;
        },
        /**
         * on success ...
         *
         * @param response
         * @param newValue
         */
        success: function(response, newValue) {
            newValue = parseInt(newValue);

            // update data-attribute
            $(this).attr('data-value', newValue);

            // update payout value formatted
            var newValuewFormatted = newValue.toLocaleString() + ' ISK';
            $(this).addClass('srp-payout-amount-changed');
            $(this).html(newValuewFormatted);

            // update fleet total srp amount
            var totalSrpAmount = 0;
            $('#tab_aasrp_srp_requests .srp-payout-amount').each(function() {
                totalSrpAmount += parseInt($(this).attr('data-value'));
            });
            $('.srp-fleet-total-amount').html(totalSrpAmount.toLocaleString() + ' ISK');
        },
        /**
         * check if input is not empty
         *
         * @param {string} value
         * @returns {string}
         */
        validate: function(value) {
            if(value === null || value === '') {
                return aaSrpSettings.translation.editableValidate;
            }
        }
    });
});
