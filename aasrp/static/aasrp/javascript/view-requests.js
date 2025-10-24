/* global aaSrpSettings, aasrpBootstrapTooltip, fetchGet, fetchPost, moment, numberFormatter */

$(document).ready(() => {
    'use strict';

    const elementSrpRequestsTable = $('#tab_aasrp_srp_requests');
    const elementBulkActions = $('div.card-srp-request-bulk-actions');

    /**
     * Table :: SRP Requests
     *
     * @type {*|jQuery}
     */

    fetchGet({url: aaSrpSettings.url.requestsForSrpLink})
        .then((data) => {
            if (data) {
                elementSrpRequestsTable.DataTable({
                    language: aaSrpSettings.dataTable.language,
                    data: data,
                    columns: [
                        // Column 0: Request Time
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
                        // Column 1: Requester
                        {
                            data: 'requester',
                            className: 'srp-request-requester'
                        },
                        // Column 2: Character
                        {
                            data: 'character_html',
                            render: {
                                display: 'display',
                                filter: 'sort',
                                sort: 'sort'
                            },
                            className: 'srp-request-character'
                        },
                        // Column 3: Request Code
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
                        // Column 4: Ship
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
                        // Column 5: Killboard Link
                        {
                            data: 'zbk_loss_amount',
                            /**
                             * Render callback
                             */
                            render: {
                                display: (data) => {
                                    return numberFormatter({
                                        value: data,
                                        locales: aaSrpSettings.locale,
                                        options: {
                                            style: 'currency',
                                            currency: 'ISK'
                                        }
                                    });
                                },
                                filter: (data) => {
                                    return data;
                                },
                                sort: (data) => {
                                    return data;
                                }
                            },
                            className: 'srp-request-zbk-loss-amount text-end'
                        },
                        // Column 6: Payout Amount
                        {
                            data: 'payout_amount_html',
                            /**
                             * Render callback
                             */
                            render: {
                                display: (data) => {
                                    return data.display.replace(
                                        '#payout_amount_localized#',
                                        numberFormatter({
                                            value: data.sort,
                                            locales: aaSrpSettings.locale,
                                            options: {
                                                style: 'currency',
                                                currency: 'ISK'
                                            }
                                        })
                                    );
                                },
                                filter: 'sort',
                                sort: 'sort'
                            },
                            className: 'srp-request-payout text-end'
                        },
                        // Column 7: Request Status Icon
                        {
                            data: 'request_status_icon',
                            className: 'srp-request-status text-center'
                        },
                        // Column 8: Actions
                        {
                            data: 'actions',
                            className: 'srp-request-actions text-end'
                        },
                        // Column 9: Bulk Actions Checkbox
                        {
                            data: 'request_code',
                            className: 'srp-request-bulk-actions-checkbox text-end',
                            render: {
                                display: (data) => {
                                    return `<div class="checkbox"><label><input class="srp-requests-bulk-action" type="checkbox" name="${data}"><span class="cr"><i class="cr-icon fas fa-check"></i></span></label></div>`;
                                }
                            }
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
                            targets: [7, 8, 9]
                        },
                        {
                            visible: false,
                            targets: [10, 11, 12]
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
                                idx: 12,
                                title: aaSrpSettings.translation.filter.character
                            },
                            {
                                idx: 10,
                                title: aaSrpSettings.translation.filter.ship
                            },
                            {
                                idx: 11,
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
                                .addClass(`cursor-pointer srp-request-${srpRequestCode}`)
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
                    },
                    initComplete: () => {
                        // Show bootstrap tooltips
                        aasrpBootstrapTooltip({selector: '#tab_aasrp_srp_requests'});

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

                        /**
                         * Bulk actions window
                         */
                        const elementBulkActionsCheckboxes = $('td.srp-request-bulk-actions-checkbox input.srp-requests-bulk-action');
                        elementBulkActionsCheckboxes.each((i, checkbox) => {
                            $(checkbox).change(() => {
                                const checkedCheckboxes = $(elementBulkActionsCheckboxes).filter(':checked');

                                if (checkedCheckboxes.length > 0) {
                                    elementBulkActions.removeClass('d-none');
                                } else {
                                    elementBulkActions.addClass('d-none');
                                }
                            });
                        });
                    }
                });
            }
        })
        .catch((error) => {
            console.error('Error fetching SRP requests:', error);
        });

    /* Helper Functions
    --------------------------------------------------------------------------------- */

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
        // const newValueFormatted = `${new Intl.NumberFormat(aaSrpSettings.locale).format(newValue)} ISK`;
        const newValueFormatted = numberFormatter({
            value: newValue,
            locales: aaSrpSettings.locale,
            options: {
                style: 'currency',
                currency: 'ISK'
            }
        });

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

        // $('.srp-fleet-total-amount').html(`${new Intl.NumberFormat(aaSrpSettings.locale).format(totalSrpAmount)} ISK`);
        $('.srp-fleet-total-amount').html(numberFormatter({
            value: totalSrpAmount,
            locales: aaSrpSettings.locale,
            options: {
                style: 'currency',
                currency: 'ISK'
            }
        }));

        // Update copy to clipboard icon value
        const copyToClipboard = element.parent().parent().find('.copy-to-clipboard-icon i');
        copyToClipboard.attr('data-clipboard-text', newValue);
    };

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
        // $('.srp-fleet-total-amount').html(`${new Intl.NumberFormat(aaSrpSettings.locale).format(totalSrpAmount)} ISK`);
        $('.srp-fleet-total-amount')
            .html(numberFormatter({
                value: totalSrpAmount,
                locales: aaSrpSettings.locale,
                options: {
                    style: 'currency',
                    currency: 'ISK'
                }
            }));

        // Update requests counts
        $('.srp-requests-total-count').html(requestsTotal);
        $('.srp-requests-pending-count').html(requestsPending);
        $('.srp-requests-approved-count').html(requestsApproved);
        $('.srp-requests-rejected-count').html(requestsRejected);
    };

    /**
     * Helper function: Unbind click event for modal confirm buttons
     *
     * @param {jQuery | HTMLElement} element
     * @private
     */
    const _unbindClickEvent = (element) => {
        // Unbind click events for the modal confirm buttons
        element.unbind('click');
    };

    /**
     * Helper function: Modal confirm action
     *
     * @param {object} data The return data from the ajax call
     * @private
     */
    const _modalConfirmAction = (data) => {
        // Reload datatable on success and update SRP status values
        if (data.success === true) {
            fetchGet({url: aaSrpSettings.url.requestsForSrpLink})
                .then((newData) => {
                    const dt = elementSrpRequestsTable.DataTable();

                    dt.clear().rows.add(newData).draw();

                    // Attempt to call the original initComplete handler (if present)
                    try {
                        const settings = dt.settings()[0];
                        const initComplete = settings && settings.oInit && settings.oInit.initComplete;

                        if (initComplete) {
                            if (Array.isArray(initComplete)) {
                                initComplete.forEach((fn) => {
                                    if (typeof fn === 'function') {
                                        fn.call(dt, settings);
                                    }
                                });
                            } else if (typeof initComplete === 'function') {
                                initComplete.call(dt, settings);
                            }
                        }
                    } catch (err) {
                        console.error('Error calling initComplete:', err);
                    }

                    _reloadSrpCalculations(newData);
                })
                .catch((error) => {
                    console.error('Error reloading SRP requests:', error);
                });
        }
    };

    /**
     * Helper function: Get selected SRP request codes
     *
     * @returns {array} An array of selected SRP request codes
     * @private
     */
    const _getSelectedSrpRequestCodes = () => {
        const elementBulkActionsCheckboxes = $('td.srp-request-bulk-actions-checkbox input.srp-requests-bulk-action');
        const checkedCheckboxes = $(elementBulkActionsCheckboxes).filter(':checked');

        return checkedCheckboxes.map((index, checkbox) => $(checkbox).attr('name')).get();
    };

    /**
     * Helper function: Get selected SRP requests
     *
     * @returns {array} An array of jQuery objects representing the selected SRP requests
     * @private
     */
    const _getSelectedSrpRequests = () => {
        const elementBulkActionsCheckboxes = $('td.srp-request-bulk-actions-checkbox input.srp-requests-bulk-action');
        const checkedCheckboxes = $(elementBulkActionsCheckboxes).filter(':checked');

        return checkedCheckboxes.map((index, checkbox) => $(checkbox)).get();
    };

    /*  Modals
    --------------------------------------------------------------------------------- */
    const modalSrpRequestDetails = $('#srp-request-details');
    const modalSrpRequestAccept = $('#srp-request-accept');
    const modalSrpRequestBulkAccept = $('#srp-request-bulk-accept');
    const modalSrpRequestAcceptRejected = $('#srp-request-accept-rejected');
    const modalSrpRequestReject = $('#srp-request-reject');
    const modalSrpRequestRemove = $('#srp-request-remove');
    const modalSrpRequestBulkRemove = $('#srp-request-bulk-remove');
    const modalFormfieldErrorClasses = 'aa-callout aa-callout-danger aasrp-form-field-errors clearfix';

    /**
     * Modal: SRP request details
     */
    modalSrpRequestDetails
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const url = button.data('link');

            fetchGet({url: url, responseIsJson: false})
                .then((data) => {
                    modalSrpRequestDetails.find('.modal-body').html(data);
                })
                .catch((error) => {
                    console.error(`Error: ${error.message}`);
                });
        })
        .on('hide.bs.modal', () => {
            modalSrpRequestDetails.find('.modal-body').text('');
        });

    /**
     * Modal: Accept SRP request
     */
    modalSrpRequestAccept
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const url = button.data('link');

            $('#modal-button-confirm-accept-request')
                .on('click', () => {
                    const form = modalSrpRequestAccept.find('form');
                    const reviserComment = form.find('textarea[name="comment"]').val();
                    const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]')
                        .val();

                    fetchPost({
                        url: url,
                        csrfToken: csrfMiddlewareToken,
                        payload: {
                            comment: reviserComment
                        },
                        responseIsJson: true
                    })
                        .then((data) => {
                            _modalConfirmAction(data);
                        })
                        .catch((error) => {
                            console.error(`Error: ${error.message}`);
                        });

                    modalSrpRequestAccept.modal('hide');
                });
        })
        .on('hide.bs.modal', () => {
            modalSrpRequestAccept.find('textarea[name="comment"]').val('');

            _unbindClickEvent($('#modal-button-confirm-accept-request'));
        });

    /**
     * Modal: Accept former rejected SRP request
     */
    modalSrpRequestAcceptRejected
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const url = button.data('link');

            $('#modal-button-confirm-accept-rejected-request')
                .on('click', () => {
                    const form = modalSrpRequestAcceptRejected.find('form');
                    const reviserComment = form.find('textarea[name="comment"]').val();
                    const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]')
                        .val();

                    if (reviserComment === '') {
                        const errorMessage = `<div class="${modalFormfieldErrorClasses}"><p>${aaSrpSettings.translation.modal.form.error.fieldRequired}</p></div>`;

                        form.find('.aasrp-form-field-errors').remove();

                        $(errorMessage).insertAfter(
                            $('textarea[name="comment"]')
                        );
                    } else {
                        fetchPost({
                            url: url,
                            csrfToken: csrfMiddlewareToken,
                            payload: {
                                comment: reviserComment
                            },
                            responseIsJson: true
                        })
                            .then((data) => {
                                _modalConfirmAction(data);
                            })
                            .catch((error) => {
                                console.error(`Error: ${error.message}`);
                            });

                        modalSrpRequestAcceptRejected.modal('hide');
                    }
                });
        })
        .on('hide.bs.modal', () => {
            modalSrpRequestAcceptRejected.find('textarea[name="comment"]').val('');

            $('.aasrp-form-field-errors').remove();
            _unbindClickEvent($('#modal-button-confirm-accept-rejected-request'));
        });

    /**
     * Modal: Reject SRP request
     */
    modalSrpRequestReject
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const url = button.data('link');

            $('#modal-button-confirm-reject-request')
                .on('click', () => {
                    const form = modalSrpRequestReject.find('form');
                    const rejectInfo = form.find('textarea[name="comment"]').val();
                    const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]')
                        .val();

                    if (rejectInfo === '') {
                        const errorMessage = `<div class="${modalFormfieldErrorClasses}"><p>${aaSrpSettings.translation.modal.form.error.fieldRequired}</p></div>`;

                        form.find('.aasrp-form-field-errors').remove();

                        $(errorMessage).insertAfter($('textarea[name="comment"]'));
                    } else {
                        fetchPost({
                            url: url,
                            csrfToken: csrfMiddlewareToken,
                            payload: {
                                comment: rejectInfo
                            },
                            responseIsJson: true
                        })
                            .then((data) => {
                                _modalConfirmAction(data);
                            })
                            .catch((error) => {
                                console.error(`Error: ${error.message}`);
                            });

                        modalSrpRequestReject.modal('hide');
                    }
                });
        })
        .on('hide.bs.modal', () => {
            modalSrpRequestReject.find('textarea[name="comment"]').val('');

            $('.aasrp-form-field-errors').remove();
            _unbindClickEvent($('#modal-button-confirm-reject-request'));
        });

    /**
     * Modal: Remove SRP request
     */
    modalSrpRequestRemove
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const url = button.data('link');

            $('#modal-button-confirm-remove-request')
                .on('click', () => {
                    fetchGet({url: url})
                        .then((data) => {
                            _modalConfirmAction(data);
                        })
                        .catch((error) => {
                            console.error(`Error: ${error.message}`);
                        });

                    modalSrpRequestRemove.modal('hide');
                });
        })
        .on('hide.bs.modal', () => {
            modalSrpRequestRemove.find('textarea[name="comment"]').val('');

            _unbindClickEvent($('#modal-button-confirm-remove-request'));
        });

    /**
     * Bulk actions: Accept selected SRP requests
     */
    modalSrpRequestBulkAccept
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const url = button.data('link');
            const form = modalSrpRequestBulkAccept.find('form');
            const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

            $('#modal-button-confirm-bulk-accept-requests')
                .on('click', () => {
                    const checkedValues = _getSelectedSrpRequestCodes();

                    fetchPost({
                        url: url,
                        csrfToken: csrfMiddlewareToken,
                        payload: {
                            srp_request_codes: checkedValues,
                        },
                        responseIsJson: true
                    })
                        .then((data) => {
                            _modalConfirmAction(data);

                            // Uncheck all checkboxes
                            const checkboxes = _getSelectedSrpRequests();

                            checkboxes.forEach((checkbox) => {
                                $(checkbox).prop('checked', false);
                            });

                            elementBulkActions.addClass('d-none');
                        })
                        .catch((error) => {
                            console.error(`Error: ${error.message}`);
                        });

                    modalSrpRequestBulkAccept.modal('hide');
                });
        })
        .on('hide.bs.modal', () => {
            _unbindClickEvent($('#modal-button-confirm-bulk-accept-requests'));
        });

    /**
     * Bulk actions: Delete selected SRP requests
     */
    modalSrpRequestBulkRemove
        .on('show.bs.modal', (event) => {
            const button = $(event.relatedTarget);
            const url = button.data('link');
            const form = modalSrpRequestBulkRemove.find('form');
            const csrfMiddlewareToken = form.find('input[name="csrfmiddlewaretoken"]').val();

            $('#modal-button-confirm-bulk-remove-requests')
                .on('click', () => {
                    const checkedValues = _getSelectedSrpRequestCodes();

                    fetchPost({
                        url: url,
                        csrfToken: csrfMiddlewareToken,
                        payload: {
                            srp_request_codes: checkedValues,
                        },
                        responseIsJson: true
                    })
                        .then((data) => {
                            _modalConfirmAction(data);

                            // Uncheck all checkboxes
                            const checkboxes = _getSelectedSrpRequests();

                            checkboxes.forEach((checkbox) => {
                                $(checkbox).prop('checked', false);
                            });

                            elementBulkActions.addClass('d-none');
                        })
                        .catch((error) => {
                            console.error(`Error: ${error.message}`);
                        });

                    modalSrpRequestBulkRemove.modal('hide');
                });
        })
        .on('hide.bs.modal', () => {
            _unbindClickEvent($('#modal-button-confirm-bulk-remove-requests'));
        });

    /* Events
    --------------------------------------------------------------------------------- */
    /**
     * Bulk actions: Clear selection
     */
    $('#aasrp-bulk-action-clear-selection')
        .on('click', () => {
            // Uncheck all checkboxes
            const checkboxes = _getSelectedSrpRequests();

            checkboxes.forEach((checkbox) => {
                $(checkbox).prop('checked', false);
            });
            // Hide bulk actions
            elementBulkActions.addClass('d-none');
        });
});
