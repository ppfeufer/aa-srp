/* global aaSrpSettings, moment */

$(document).ready(() => {
    'use strict';

    const elementSrpRequestsTable = $('#tab_aasrp_srp_requests');

    /**
     * Table :: SRP Requests
     */
    const srpRequestsTable = elementSrpRequestsTable.DataTable({
        ajax: {
            url: aaSrpSettings.url.requestsForSrpLink,
            dataSrc: '',
            cache: false
        },
        columns: [
            {
                data: 'request_time',
                render: (data, type, row) => {
                    return moment(data).utc().format(aaSrpSettings.datetimeFormat);
                },
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
                render: (data, type, row, meta) => {
                    if (type === 'display') {
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
                render: (data, type, row, meta) => {
                    if (type === 'display') {
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
            {data: 'character'}
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
                    idx: 1
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
        createdRow: (row, data, rowIndex) => {
            // Row id attr
            $(row).attr('data-row-id', rowIndex);
            $(row).attr('data-srp-request-code', data.request_code);
            $(row).addClass('srp-request-status-' + data.request_status.toLowerCase());

            // add class and data attribute to the payout span
            $(row).find('span.srp-payout-amount').addClass(
                'srp-request-' + data.request_code
            );
            $(row).find('span.srp-payout-amount').attr(
                'data-params', '{csrfmiddlewaretoken:\'' + aaSrpSettings.csrfToken + '\'}'
            );
            $(row).find('span.srp-payout-amount').attr('data-pk', data.request_code);
            $(row).find('span.srp-payout-amount').attr('data-value', data.payout_amount);
            $(row).find('span.srp-payout-amount').attr(
                'data-url', aaSrpSettings.url.changeSrpAmount.replace(
                    'SRP_REQUEST_CODE',
                    data.request_code
                )
            );
        }
    });

    /**
     * Helper function: Refresh the Payout Amount field
     *
     * @param element
     * @param {int} newValue
     * @private
     */
    const _refreshSrpAmountField = (element, newValue) => {
        newValue = parseInt(newValue);

        // update data-attribute
        element.attr('data-value', newValue);

        // update payout value formatted
        const newValuewFormatted = newValue.toLocaleString() + ' ISK';

        element.addClass('srp-payout-amount-changed');
        element.html(newValuewFormatted);

        // update fleet total srp amount
        let totalSrpAmount = 0;

        $('#tab_aasrp_srp_requests .srp-request-status-approved .srp-payout-amount').each((i, payoutElement) => {
            totalSrpAmount += parseInt(payoutElement.getAttribute('data-value'));
        });

        $('.srp-fleet-total-amount').html(totalSrpAmount.toLocaleString() + ' ISK');
    };

    /**
     * Make srp payout field editable for pending requests
     */
    elementSrpRequestsTable.editable({
        container: 'body',
        selector: '.srp-request-status-pending .srp-payout-amount', // Only for pending requests
        title: aaSrpSettings.translation.changeSrpPayoutHeader,
        type: 'number',
        placement: 'top',
        /**
         * @param value
         * @param response
         * @returns {boolean}
         */
        display: (value, response) => {
            return false;
        },
        /**
         * on success ...
         *
         * Arrow functions don't work here since we need $(this)
         *
         * @param response
         * @param newValue
         */
        success: function(response, newValue) {
            _refreshSrpAmountField($(this), newValue);
        },
        /**
         * check if input is not empty
         *
         * @param {string} value
         * @returns {string}
         */
        validate: (value) => {
            if (value === null || value === '') {
                return aaSrpSettings.translation.editableValidate;
            }
        }
    });

    /**
     * Make srp payout field editable for rejected requests,
     * in case they get approved later on
     */
    elementSrpRequestsTable.editable({
        container: 'body',
        selector: '.srp-request-status-rejected .srp-payout-amount', // Only for rejected requests
        title: aaSrpSettings.translation.changeSrpPayoutHeader,
        type: 'number',
        placement: 'top',
        /**
         * @param value
         * @param response
         * @returns {boolean}
         */
        display: (value, response) => {
            return false;
        },
        /**
         * on success ...
         *
         * Arrow functions don't work here since we need $(this)
         *
         * @param response
         * @param newValue
         */
        success: function(response, newValue) {
            _refreshSrpAmountField($(this), newValue);
        },
        /**
         * check if input is not empty
         *
         * @param {string} value
         * @returns {string}
         */
        validate: (value) => {
            if (value === null || value === '') {
                return aaSrpSettings.translation.editableValidate;
            }
        }
    });

    /**
     * Modals
     */
    const modalSrpRequestDetails = $('#srp-request-details');
    const modalSrpRequestAccept = $('#srp-request-accept');
    const modalSrpRequestReject = $('#srp-request-reject');
    const modalSrpRequestRemove = $('#srp-request-remove');

    // SRP request details
    modalSrpRequestDetails.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const name = button.data('modal-title');
        const url = button.data('link');
        const confirmButtonText = button.data('modal-button-confirm');

        modalSrpRequestDetails.find('.modal-title').text(name);
        modalSrpRequestDetails.find('#modal-button-request-details-confirm').html(confirmButtonText);

        $.get({
            url: url,
            success: (data) => {
                const modalBody = data;

                modalSrpRequestDetails.find('.modal-body').html(modalBody);
            }
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestDetails.find('.modal-title').text('');
        modalSrpRequestDetails.find('.modal-body').text('');
    });

    // accept SRP request
    modalSrpRequestAccept.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const name = button.data('modal-title');
        const url = button.data('link');
        const confirmButtonText = button.data('modal-button-confirm');
        const cancelButtonText = button.data('modal-button-cancel');
        const confirmButtonClasses = button.data('modal-button-confirm-classes');
        const body = button.data('modal-body');

        modalSrpRequestAccept.find('.modal-title').text(name);
        modalSrpRequestAccept.find('#modal-button-confirm-accept-request').addClass(confirmButtonClasses);
        modalSrpRequestAccept.find('#modal-button-confirm-accept-request').html(confirmButtonText);
        modalSrpRequestAccept.find('#modal-button-cancel-accept-request').html(cancelButtonText);
        modalSrpRequestAccept.find('.modal-body').text(body);

        $('#modal-button-confirm-accept-request').on('click', (event) => {
            $.get(url, (data, status) => {
                // reload datatable on success and update srp status values
                if (data['0'].success === true) {
                    srpRequestsTable.ajax.reload((tableData) => {
                        let totalSrpAmount = 0;
                        let requestsTotal = 0;
                        let requestsPending = 0;
                        let requestsApproved = 0;
                        let requestsRejected = 0;

                        $.each(tableData, (i, item) => {
                            requestsTotal += 1;

                            if (item.request_status === 'Pending') {
                                requestsPending += 1;
                            }

                            if (item.request_status === 'Approved') {
                                totalSrpAmount += parseInt(item.payout_amount);
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
    }).on('hide.bs.modal', () => {
        modalSrpRequestAccept.find('textarea[name="reject_info"]').val('');

        $('#modal-button-confirm-accept-request').unbind('click');
    });

    // reject SRP request
    modalSrpRequestReject.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        $('#modal-button-confirm-reject-request').on('click', () => {
            const form = modalSrpRequestReject.find('form');
            const rejectInfo = form.find('textarea[name="reject_info"]').val();
            const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

            if (rejectInfo === '') {
                const errorMessage = '<div class="aasrp-form-field-errors clearfix">' +
                    '<div class="aasrp-form-field-error clearfix">' +
                    aaSrpSettings.translation.modal.rejectRequest.body.fieldRequired +
                    '</div>' +
                    '</div>';

                form.find('.aasrp-form-field-errors').remove();

                $(errorMessage).insertAfter($('textarea[name="reject_info"]'));
            }

            if (rejectInfo !== '') {
                const posting = $.post(
                    url,
                    {
                        reject_info: rejectInfo,
                        csrfmiddlewaretoken: csrfMiddlewareToken
                    }
                );

                posting.done((data) => {
                    // $('#modal-button-cancel-reject-request').click();

                    if (data['0'].success === true) {
                        srpRequestsTable.ajax.reload((tableData) => {
                            let totalSrpAmount = 0;
                            let requestsTotal = 0;
                            let requestsPending = 0;
                            let requestsApproved = 0;
                            let requestsRejected = 0;

                            $.each(tableData, (i, item) => {
                                requestsTotal += 1;

                                if (item.request_status === 'Pending') {
                                    requestsPending += 1;
                                }

                                if (item.request_status === 'Approved') {
                                    totalSrpAmount += parseInt(item.payout_amount);
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

                modalSrpRequestReject.modal('toggle');
            }
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestReject.find('textarea[name="reject_info"]').val('');

        $('#modal-button-confirm-reject-request').unbind('click');
    });

    // remove SRP request
    modalSrpRequestRemove.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const name = button.data('modal-title');
        const url = button.data('link');
        const confirmButtonText = button.data('modal-button-confirm');
        const cancelButtonText = button.data('modal-button-cancel');
        const confirmButtonClasses = button.data('modal-button-confirm-classes');
        const body = button.data('modal-body');

        modalSrpRequestRemove.find('.modal-title').text(name);
        modalSrpRequestRemove.find('#modal-button-confirm-remove-request').addClass(confirmButtonClasses);
        modalSrpRequestRemove.find('#modal-button-confirm-remove-request').html(confirmButtonText);
        modalSrpRequestRemove.find('#modal-button-cancel-remove-request').html(cancelButtonText);
        modalSrpRequestRemove.find('.modal-body').text(body);

        $('#modal-button-confirm-remove-request').on('click', (event) => {
            $.get(url, (data, status) => {
                // reload datatable on success and update srp status values
                if (data['0'].success === true) {
                    srpRequestsTable.ajax.reload((tableData) => {
                        let totalSrpAmount = 0;
                        let requestsTotal = 0;
                        let requestsPending = 0;
                        let requestsApproved = 0;
                        let requestsRejected = 0;

                        $.each(tableData, (i, item) => {
                            requestsTotal += 1;

                            if (item.request_status === 'Pending') {
                                requestsPending += 1;
                            }

                            if (item.request_status === 'Approved') {
                                totalSrpAmount += parseInt(item.payout_amount);
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
    }).on('hide.bs.modal', () => {
        modalSrpRequestRemove.find('textarea[name="reject_info"]').val('');

        $('#modal-button-confirm-remove-request').unbind('click');
    });
});
