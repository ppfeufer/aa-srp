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
                ),
                className: 'srp-request-time'
            },
            {
                data: 'requester',
                className: 'srp-request-requester'
            },
            {
                data: 'character_html',
                render: {
                    display: 'display',
                    _: 'sort'
                },
                className: 'srp-request-character'
            },
            {
                data: 'request_code',
                className: 'srp-request-code'
            },
            {
                data: 'ship_html',
                render: {
                    display: 'display',
                    _: 'sort'
                },
                className: 'srp-request-ship'
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
                className: 'srp-request-zbk-loss-amount text-right'
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
                className: 'srp-request-payout text-right'
            },
            {
                data: 'request_status_icon',
                className: 'srp-request-status text-center'
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
            {data: 'character'},
        ],
        columnDefs: [
            {
                orderable: false,
                targets: [7, 8]
            },
            {
                visible: false,
                targets: [9, 10, 11]
            },
            {
                width: 115,
                targets: [8]
            }
        ],
        order: [
            [0, 'asc']
        ],
        filterDropDown: {
            columns: [
                {
                    idx: 1,
                },
                {
                    idx: 11,
                    title: aaSrpSettings.translation.filter.character
                },
                {
                    idx: 9,
                    title: aaSrpSettings.translation.filter.ship
                },
                {
                    idx: 10,
                    title: aaSrpSettings.translation.filter.requestStatus
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
            $(row).attr('data-srp-request-code', data.request_code);

            // add class and data attribute to the payout span
            $(row).find('span.srp-payout-amount').addClass(
                'srp-request-' + data.request_code
            );
            $(row).find('span.srp-payout-amount').attr(
                'data-params', '{csrfmiddlewaretoken:\''+  aaSrpSettings.csrfToken + '\'}'
            );
            $(row).find('span.srp-payout-amount').attr('data-pk', data.request_code);
            $(row).find('span.srp-payout-amount').attr('data-value', data.payout_amount);
            $(row).find('span.srp-payout-amount').attr(
                'data-url', aaSrpSettings.url.changeSrpAmount.replace(
                    'SRP_REQUEST_CODE',
                    data.request_code
                )
            );
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

    /**
     * Modals
     */
    $('#srp-request-details')
        .on('show.bs.modal', function(event) {
            var button = $(event.relatedTarget);
            var modal = $(this);

            var name = button.data('modal-title');
            var url = button.data('link');
            var confirmButtonText = button.data('modal-button-confirm');
            var body = button.data('modal-body');

            modal.find('.modal-title').text(name);
            modal.find('#modal-button-request-details-confirm').html(confirmButtonText);
            modal.find('.modal-body').text(body);

            $.get({
                url: url,
                success: function(data) {
                    var modalBody = '';

                    // requestor
                    modalBody += '<div class="clearfix modal-srp-details modal-srp-details-requester">' +
                        '<div class="col-sm-6"><p><b>' + aaSrpSettings.translation.modal.srpDetails.body.requestor + ':</b></p><p>' + data.requester + '</p></div>' +
                        '<div class="col-sm-6"><p><b>' + aaSrpSettings.translation.modal.srpDetails.body.character + ':</b></p><p>' + data.character + '</p></div>' +
                        '</div>';

                    // ship and killmail
                    modalBody += '<div class="clearfix modal-srp-details modal-srp-details-ship">' +
                        '<div class="col-sm-12"><p><b>' + aaSrpSettings.translation.modal.srpDetails.body.ship + ':</b></p><p>' + data.killboard_link + '</p></div>' +
                        '</div>';

                    // additional info
                    modalBody += '<div class="clearfix modal-srp-details modal-srp-details-additional-information">' +
                        '<div class="col-sm-12"><p><b>' + aaSrpSettings.translation.modal.srpDetails.body.additionalInformation + ':</b></p><p>' + data.additional_info + '</p></div>' +
                        '</div>';

                    if (data.reject_info !== '') {
                        // reject info
                        modalBody += '<div class="clearfix modal-srp-details modal-srp-details-additional-information">' +
                            '<div class="col-sm-12"><p><b>' + aaSrpSettings.translation.modal.srpDetails.body.rejectInformation + ':</b></p><p>' + data.reject_info + '</p></div>' +
                            '</div>';
                    }

                    // add to modal body
                    modal.find('.modal-body').html(modalBody);
                }
            });
        })
        .on('hide.bs.modal', function() {
            var modal = $(this);

            modal.find('.modal-title').text('');
            modal.find('.modal-body').text('');
        });

    $('#srp-request-accept')
        .on('show.bs.modal', function(event) {
            var button = $(event.relatedTarget);
            var modal = $(this);

            var name = button.data('modal-title');
            var url = button.data('link');
            var confirmButtonText = button.data('modal-button-confirm');
            var cancelButtonText = button.data('modal-button-cancel');
            var confirmButtonClasses = button.data('modal-button-confirm-classes');
            var body = button.data('modal-body');

            modal.find('.modal-title').text(name);
            modal.find('#modal-button-confirm-accept-request').addClass(confirmButtonClasses);
            modal.find('#modal-button-confirm-accept-request').html(confirmButtonText);
            modal.find('#modal-button-cancel-accept-request').html(cancelButtonText);
            modal.find('.modal-body').text(body);

            $('#modal-button-confirm-accept-request').on('click', function(event) {
                $.get(url, function(data, status) {
                    // reload datatable on success and update srp status values
                    if (data['0'].success === true) {
                        srpRequestsTable.ajax.reload(function(tableData) {
                            var totalSrpAmount = 0;
                            var requestsTotal = 0;
                            var requestsPending = 0;
                            var requestsApproved = 0;
                            var requestsRejected = 0;

                            $.each(tableData, function(i, item) {
                                totalSrpAmount += parseInt(item.payout_amount);
                                requestsTotal += 1;

                                if (item.request_status === 'Pending') {
                                    requestsPending += 1;
                                }

                                if (item.request_status === 'Approved') {
                                    requestsApproved += 1;
                                }

                                if (item.request_status === 'Rejected') {
                                    requestsRejected += 1;
                                }
                            });

                            // update fleet total srp amount
                            $('.srp-fleet-total-amount').html(
                                totalSrpAmount.toLocaleString() + ' ISK'
                            );

                            // update requests counts
                            $('.srp-requests-total-count').html(
                                requestsTotal
                            );
                            $('.srp-requests-pending-count').html(
                                requestsPending
                            );
                            $('.srp-requests-approved-count').html(
                                requestsApproved
                            );
                            $('.srp-requests-rejected-count').html(
                                requestsRejected
                            );
                        });
                    }
                });
            });
        });

    $('#srp-request-reject')
        .on('show.bs.modal', function(event) {
            var button = $(event.relatedTarget);
            var modal = $(this);
            var url = button.data('link');

            $('#modal-button-confirm-reject-request').on('click', function() {
                var form = modal.find('form');
                var rejectInfo = form.find('textarea[name="reject_info"]').val();
                var csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

                if (rejectInfo === '') {
                    var errorMessage = '<div class="aasrp-form-field-errors clearfix">' +
                        '<div class="aasrp-form-field-error clearfix">' +
                        aaSrpSettings.translation.modal.rejectRequest.body.fieldRequired +
                        '</div>' +
                        '</div>';

                    form.find('.aasrp-form-field-errors').remove();
                    $(errorMessage).insertAfter($('textarea[name="reject_info"]'));
                }

                if (rejectInfo !== '') {
                    var posting = $.post(
                        url,
                        {
                            reject_info: rejectInfo,
                            csrfmiddlewaretoken: csrfMiddlewareToken
                        }
                    );

                    posting.done(function(data) {
                        // $('#modal-button-cancel-reject-request').click();

                        if (data['0'].success === true) {
                            srpRequestsTable.ajax.reload(function(tableData) {
                                var totalSrpAmount = 0;
                                var requestsTotal = 0;
                                var requestsPending = 0;
                                var requestsApproved = 0;
                                var requestsRejected = 0;

                                $.each(tableData, function(i, item) {
                                    totalSrpAmount += parseInt(item.payout_amount);
                                    requestsTotal += 1;

                                    if (item.request_status === 'Pending') {
                                        requestsPending += 1;
                                    }

                                    if (item.request_status === 'Approved') {
                                        requestsApproved += 1;
                                    }

                                    if (item.request_status === 'Rejected') {
                                        requestsRejected += 1;
                                    }
                                });

                                // update fleet total srp amount
                                $('.srp-fleet-total-amount').html(
                                    totalSrpAmount.toLocaleString() + ' ISK'
                                );

                                // update requests counts
                                $('.srp-requests-total-count').html(
                                    requestsTotal
                                );
                                $('.srp-requests-pending-count').html(
                                    requestsPending
                                );
                                $('.srp-requests-approved-count').html(
                                    requestsApproved
                                );
                                $('.srp-requests-rejected-count').html(
                                    requestsRejected
                                );
                            });
                        }
                    });

                    modal.modal('toggle');
                }
            });
        })
        .on('hide.bs.modal', function() {
            var modal = $(this);

            modal.find('textarea[name="reject_info"]').val('');
            $('#modal-button-confirm-reject-request').unbind('click');
        });
});
