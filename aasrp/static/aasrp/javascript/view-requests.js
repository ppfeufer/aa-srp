/* global aaSrpSettings, bootstrap, moment */

$(document).ready(() => {
    'use strict';

    const elementSrpRequestsTable = $('#tab_aasrp_srp_requests');

    /**
     * Table :: SRP Requests
     *
     * @type {*|jQuery}
     */
    const srpRequestsTable = elementSrpRequestsTable.DataTable({
        language: aaSrpSettings.dataTable.language,
        ajax: {
            url: aaSrpSettings.url.requestsForSrpLink,
            dataSrc: '',
            cache: false
        },
        columns: [
            {
                data: 'request_time',
                /**
                 * Render callback
                 */
                render: {
                    /**
                     * Display callback
                     *
                     * @param {int|string} data
                     * @returns {string|*}
                     * @private
                     */
                    display: (data) => {
                        return data === null ? '' : moment(data).utc().format(
                            aaSrpSettings.datetimeFormat
                        );
                    },
                    /**
                     * Sort callback
                     *
                     * @param {int|string} data
                     * @returns {string|*}
                     */
                    sort: (data) => {
                        return data === null ? '' : data;
                    }
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
                    filter: 'sort',
                    sort: 'sort'
                },
                className: 'srp-request-character'
            },
            {
                data: 'request_code_html',
                /**
                 * Render callback
                 */
                render:  {
                    display: 'display',
                    filter: 'sort',
                    sort: 'sort'
                },
                className: 'srp-request-code'
            },
            {
                data: 'ship_html',
                render: {
                    display: 'display',
                    filter: 'sort',
                    sort: 'sort'
                },
                className: 'srp-request-ship'
            },
            // {data: 'zkb_link'},
            {
                data: 'zkb_loss_amount_html',
                /**
                 * Render callback
                 */
                render: {
                    display: 'display',
                    filter: 'sort',
                    sort: 'sort'
                },
                className: 'srp-request-zbk-loss-amount text-end'
            },
            {
                data: 'payout_amount_html',
                /**
                 * Render callback
                 */
                render: {
                    display: 'display',
                    filter: 'sort',
                    sort: 'sort'
                },
                className: 'srp-request-payout text-end'
            },
            {
                data: 'request_status_icon',
                className: 'srp-request-status text-center'
            },
            {
                data: 'actions',
                className: 'srp-request-actions text-end'
            },

            /**
             * Hidden columns
             */
            {data: 'ship'},
            {data: 'request_status_translated'},
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
            bootstrap: true,
            bootstrap_version: 5,
        },
        paging: false,
        /**
         * When ever a row is created …
         *
         * @param row
         * @param data
         * @param rowIndex
         */
        createdRow: (row, data, rowIndex) => {
            const srpRequestCode = data.request_code;
            const srpRequestStatus = data.request_status.toLowerCase();
            const srpRequestPayoutAmount = data.payout_amount;

            // Row id attr
            $(row)
                .attr('data-row-id', rowIndex)
                .attr('data-srp-request-code', srpRequestCode)
                .addClass('srp-request-status-' + srpRequestStatus);

            $(row)
                .find('span.srp-payout-amount')
                .attr('data-value', srpRequestPayoutAmount);

            // Add class and data attribute to the payout span
            if (srpRequestStatus === 'pending' || srpRequestStatus === 'rejected') {
                $(row)
                    .find('td.srp-request-payout')
                    .addClass('srp-request-payout-amount-editable');

                $(row)
                    .find('span.srp-payout-tooltip')
                    .attr(
                        'data-bs-tooltip',
                        'aa-srp'
                    )
                    .attr(
                        'title',
                        aaSrpSettings.translation.changeSrpPayoutAmount
                    );

                $(row)
                    .find('span.srp-payout-amount')
                    .addClass('srp-request-' + srpRequestCode)
                    .attr('data-pk', srpRequestCode)
                    .attr(
                        'data-params',
                        `{csrfmiddlewaretoken:'${aaSrpSettings.csrfToken}'}`
                    )
                    .attr(
                        'data-url',
                        aaSrpSettings.url.changeSrpAmount.replace(
                            'SRP_REQUEST_CODE',
                            srpRequestCode
                        )
                    );
            }
        }
    });

    /**
     * Helper function: Refresh the Payout Amount field
     *
     * @param element
     * @param {int|string} newValue
     * @private
     */
    const _refreshSrpAmountField = (element, newValue) => {
        newValue = parseInt(newValue);

        // Update payout value formatted
        const newValueFormatted = `${new Intl.NumberFormat(aaSrpSettings.locale).format(newValue)} ISK`;

        // Update the element
        element
            .attr('data-value', newValue)
            .addClass('srp-payout-amount-changed')
            .html(newValueFormatted);

        // Update fleet total SRP amount
        let totalSrpAmount = 0;
        const elementSrpAmount = $(
            '#tab_aasrp_srp_requests .srp-request-status-approved .srp-payout-amount'
        );

        elementSrpAmount.each((i, payoutElement) => {
            totalSrpAmount += parseInt(payoutElement.getAttribute('data-value'));
        });

        $('.srp-fleet-total-amount').html(`${new Intl.NumberFormat(aaSrpSettings.locale).format(totalSrpAmount)} ISK`);

        // Update copy to clipboard icon value
        const copyToClipboard = element.parent().parent().find('.copy-to-clipboard-icon i');
        copyToClipboard.attr('data-clipboard-text', newValue);
    };

    /**
     * When the DataTable has finished rendering and is fully initialized
     */
    srpRequestsTable.on('draw', () => {
        // Make the SRP payout field editable for pending and rejected requests.
        elementSrpRequestsTable.editable({
            container: 'body',
            selector: '.srp-request-payout-amount-editable .srp-payout-amount',
            title: aaSrpSettings.translation.changeSrpPayoutHeader,
            type: 'number',
            placement: 'top',
            /**
             * @returns {boolean}
             */
            display: () => {
                return false;
            },
            /**
             * On success …
             *
             * Arrow functions don't work here since we need `$(this)`.
             *
             * @param response
             * @param newValue
             */
            success: function (response, newValue) {
                _refreshSrpAmountField($(this), newValue);
            },
            /**
             * Check if input is not empty
             *
             * @param {string} value
             * @returns {string}
             */
            validate: (value) => {
                if (value === '') {
                    return aaSrpSettings.translation.editableValidate;
                }
            }
        });

        // Show bootstrap tooltips
        [].slice.call(
            document.querySelectorAll('[data-bs-tooltip="aa-srp"]')
        ).map((tooltipTriggerEl) => {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    });

    /**
     * Helper function: Reloading SRP calculation in our DataTable
     *
     * @param {object} tableData The DataTable data
     * @private
     */
    const _reloadSrpCalculations = (tableData) => {
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

        // Update fleet total SRP amount
        $('.srp-fleet-total-amount').html(`${new Intl.NumberFormat(aaSrpSettings.locale).format(totalSrpAmount)} ISK`);

        // Update requests counts
        $('.srp-requests-total-count').html(requestsTotal);
        $('.srp-requests-pending-count').html(requestsPending);
        $('.srp-requests-approved-count').html(requestsApproved);
        $('.srp-requests-rejected-count').html(requestsRejected);
    };

    /**
     * Modals
     */
    const modalSrpRequestDetails = $('#srp-request-details');
    const modalSrpRequestAccept = $('#srp-request-accept');
    const modalSrpRequestAcceptRejected = $('#srp-request-accept-rejected');
    const modalSrpRequestReject = $('#srp-request-reject');
    const modalSrpRequestRemove = $('#srp-request-remove');

    /**
     * Helper function: Modal confirm action
     *
     * @param {object} data The return data from the ajax call
     * @private
     */
    const _modalConfirmAction = (data) => {
        // Reload datatable on success and update SRP status values
        if (data.success === true) {
            srpRequestsTable.ajax.reload((tableData) => {
                _reloadSrpCalculations(tableData);
            });
        }
    };

    /**
     * Modal: SRP request details
     */
    modalSrpRequestDetails.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        $.get({
            url: url,
            success: (data) => {
                modalSrpRequestDetails.find('.modal-body').html(data);
            }
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestDetails.find('.modal-body').text('');
    });

    /**
     * Modal: Accept SRP request
     */
    modalSrpRequestAccept.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        $('#modal-button-confirm-accept-request').on('click', () => {
            const form = modalSrpRequestAccept.find('form');
            const reviserComment = form.find('textarea[name="comment"]').val();
            const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]')
                .val();

            const posting = $.post(
                url,
                {
                    comment: reviserComment,
                    csrfmiddlewaretoken: csrfMiddlewareToken
                }
            );

            posting.done((data) => {
                _modalConfirmAction(data);
            });

            modalSrpRequestAccept.modal('hide');
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestAccept.find('textarea[name="comment"]').val('');

        $('#modal-button-confirm-accept-request').unbind('click');
    });

    /**
     * Modal: Accept former rejected SRP request
     */
    modalSrpRequestAcceptRejected.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        $('#modal-button-confirm-accept-rejected-request').on('click', () => {
            const form = modalSrpRequestAcceptRejected.find('form');
            const reviserComment = form.find('textarea[name="comment"]').val();
            const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]')
                .val();

            if (reviserComment === '') {
                const errorMessage = `<div class="aa-callout aa-callout-danger aasrp-form-field-errors clearfix"><p>${aaSrpSettings.translation.modal.form.error.fieldRequired}</p></div>`;

                form.find('.aasrp-form-field-errors').remove();

                $(errorMessage).insertAfter(
                    $('textarea[name="comment"]')
                );
            } else {
                const posting = $.post(
                    url,
                    {
                        comment: reviserComment,
                        csrfmiddlewaretoken: csrfMiddlewareToken
                    }
                );

                posting.done((data) => {
                    _modalConfirmAction(data);
                });

                modalSrpRequestAcceptRejected.modal('hide');
            }
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestAcceptRejected.find('textarea[name="comment"]').val('');

        $('.aasrp-form-field-errors').remove();
        $('#modal-button-confirm-accept-rejected-request').unbind('click');
    });

    /**
     * Modal: Reject SRP request
     */
    modalSrpRequestReject.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        $('#modal-button-confirm-reject-request').on('click', () => {
            const form = modalSrpRequestReject.find('form');
            const rejectInfo = form.find('textarea[name="comment"]').val();
            const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]')
                .val();

            if (rejectInfo === '') {
                const errorMessage = `<div class="aa-callout aa-callout-danger aasrp-form-field-errors clearfix"><p>${aaSrpSettings.translation.modal.form.error.fieldRequired}</p></div>`;

                form.find('.aasrp-form-field-errors').remove();

                $(errorMessage).insertAfter($('textarea[name="comment"]'));
            } else {
                const posting = $.post(
                    url,
                    {
                        comment: rejectInfo,
                        csrfmiddlewaretoken: csrfMiddlewareToken
                    }
                );

                posting.done((data) => {
                    _modalConfirmAction(data);
                });

                modalSrpRequestReject.modal('hide');
            }
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestReject.find('textarea[name="comment"]').val('');

        $('.aasrp-form-field-errors').remove();
        $('#modal-button-confirm-reject-request').unbind('click');
    });

    /**
     * Modal: Remove SRP request
     */
    modalSrpRequestRemove.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('link');

        $('#modal-button-confirm-remove-request').on('click', () => {
            $.get(url, (data) => {
                _modalConfirmAction(data);
            });

            modalSrpRequestRemove.modal('hide');
        });
    }).on('hide.bs.modal', () => {
        modalSrpRequestRemove.find('textarea[name="comment"]').val('');

        $('#modal-button-confirm-remove-request').unbind('click');
    });
});
