/* global _bootstrapTooltip, _copyToClipboard, _filterDataTable, _removeSearchFromColumnControl, _showToast, aaSrpSettings, DataTable, fetchGet, fetchPost, moment, numberFormatter */

$(document).ready(() => {
    'use strict';

    const element = {
        srpRequestsTable: $('#table_aasrp_srp_requests'),
        bulkActions: $('div.card-srp-request-bulk-actions'),
        totalSrpCost: $('#srp-fleet-total-cost')
    };

    const editablePayoutSelector = '.srp-request-payout-amount-editable .srp-payout-amount';

    // Set initial total SRP cost value
    const totalSrpCost = element.totalSrpCost.data('total-srp-cost') || 0;
    element.totalSrpCost.html(numberFormatter({
        value: totalSrpCost,
        locales: aaSrpSettings.locale,
        options: {
            style: 'currency',
            currency: 'ISK'
        }
    }));

    /**
     * Update total notifications badge in sidebar menu
     */
    const updateTotalNotificationsBadge = () => {
        const badges = [];
        let notificationCount = 0;

        document.querySelectorAll('#sidebar-menu .badge').forEach((b) => {
            const li = b.closest('li');

            if (!li || !li.querySelector('ul.collapse')) {
                badges.push(b);
                notificationCount += parseInt(b.textContent);
            }
        });

        if (badges.length > 0 && notificationCount > 0) {
            const notificationBadge = $('span.sidemenu-total-notifications-badge');

            if (notificationCount === 0) {
                notificationBadge.remove();

                return;
            }

            notificationBadge.text(String(notificationCount));
        }
    };

    /**
     * Table :: SRP Requests
     *
     * @type {*|jQuery}
     */
    fetchGet({url: aaSrpSettings.url.requestsForSrpLink})
        .then((data) => {
            if (data) {
                const payoutEditableMode = aaSrpSettings.payoutEditableMode || 'popup';
                const columnDefs = [
                    {
                        targets: [0, 4, 5],
                        columnControl: _removeSearchFromColumnControl(
                            aaSrpSettings.dataTables.columnControl,
                            1
                        )
                    },
                    {
                        targets: [7, 8, 9],
                        orderable: false,
                        columnControl: [
                            {target: 0, content: []},
                            {target: 1, content: []}
                        ]
                    },
                    {
                        target: 8,
                        width: 120
                    },
                    {
                        target: 10,
                        visible: false
                    }
                ];

                // If the payout field is editable inline, we need to increase the width of the column to accommodate the input field.
                if (payoutEditableMode === 'inline') {
                    columnDefs.push({
                        target: 5,
                        width: 325
                    });
                }

                const dt = new DataTable(element.srpRequestsTable, { // eslint-disable-line no-unused-vars
                    ...aaSrpSettings.dataTables,
                    data: data,
                    columns: [
                        // Column 0: Request Time
                        {
                            data: {
                                display: (data) => moment(data.request_time).utc().format(aaSrpSettings.datetimeFormat),
                                filter: (data) => data.request_time,
                                sort: (data) => moment(data.request_time).unix()
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
                            data: {
                                display: (data) => data.character_html.display,
                                filter: (data) => data.character_html.sort,
                                sort: (data) => data.character_html.sort
                            },
                            className: 'srp-request-character'
                        },
                        // Column 3: Ship
                        {
                            data: {
                                display: (data) => data.ship_html.display,
                                filter: (data) => data.ship_html.sort,
                                sort: (data) => data.ship_html.sort
                            },
                            className: 'srp-request-ship'
                        },
                        // Column 4: ISK lost
                        {
                            data: {
                                display: (data) => numberFormatter({
                                    value: data.zbk_loss_amount,
                                    locales: aaSrpSettings.locale,
                                    options: {
                                        style: 'currency',
                                        currency: 'ISK'
                                    }
                                }),
                                filter: (data) => data.zbk_loss_amount,
                                sort: (data) => data.zbk_loss_amount
                            },
                            className: 'srp-request-zbk-loss-amount text-end'
                        },
                        // Column 5: Payout Amount
                        {
                            data: {
                                display: (data) => data.payout_amount_html.display.replace(
                                    '#payout_amount_localized#',
                                    numberFormatter({
                                        value: data.payout_amount_html.sort,
                                        locales: aaSrpSettings.locale,
                                        options: {
                                            style: 'currency',
                                            currency: 'ISK'
                                        }
                                    })
                                ),
                                filter: (data) => data.payout_amount_html.sort,
                                sort: (data) => data.payout_amount_html.sort
                            },
                            className: 'srp-request-payout text-end'
                        },
                        // Column 6: Additional Information (first line)
                        {
                            data: {
                                display: (data) => data.additional_info_html.display,
                                filter: (data) => data.additional_info_html.sort,
                                sort: (data) => data.additional_info_html.sort
                            },
                            className: 'srp-request-additional-info'
                        },
                        // Column 7: Request Status Icon
                        {
                            data: {
                                display: (data) => data.request_status_icon,
                                sort: (data) => data.request_status
                            },
                            className: 'srp-request-status text-center'
                        },
                        // Column 8: Actions
                        {
                            data: 'actions',
                            className: 'srp-request-actions text-end'
                        },
                        // Column 9: Bulk Actions Checkbox
                        {
                            data: {
                                display: (data) => {
                                    return `<div class="checkbox"><label><input class="srp-requests-bulk-action" type="checkbox" name="${data.request_code}"><span class="cr"><i class="cr-icon fas fa-check"></i></span></label></div>`;
                                }
                            },
                            className: 'srp-request-bulk-actions-checkbox text-end'
                        },
                        // Hidden columns
                        // Column 10: Request Code
                        {
                            data: {
                                display: (data) => data.request_code_html.display,
                                filter: (data) => data.request_code_html.sort,
                                sort: (data) => data.request_code_html.sort
                            },
                            className: 'srp-request-code'
                        }
                    ],
                    columnDefs: columnDefs,
                    order: [
                        [0, 'asc']
                    ],
                    /**
                     * When ever a row is created…
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
                        const dt = element.srpRequestsTable.DataTable();

                        const _filters = [
                            ['#aasrp-srp-request-filter-all', () => true],
                            ['#aasrp-srp-request-filter-pending', (rowData) => rowData.request_status === 'Pending'],
                            ['#aasrp-srp-request-filter-approved', (rowData) => rowData.request_status === 'Approved'],
                            ['#aasrp-srp-request-filter-rejected', (rowData) => rowData.request_status === 'Rejected']
                        ];

                        _filters.forEach(([selector, predicate]) => _filterDataTable(dt, selector, predicate));

                        // Show bootstrap tooltips
                        _bootstrapTooltip({selector: '#tab_aasrp_srp_requests'});

                        dt.on('draw', () => {
                            _bootstrapTooltip({selector: '#tab_aasrp_srp_requests'});
                        });

                        // Make the SRP payout field editable for pending and rejected requests.
                        element.srpRequestsTable.editable({
                            // container: '.aa-srp',
                            selector: editablePayoutSelector,
                            title: aaSrpSettings.translation.changeSrpPayoutHeader,
                            type: 'number',
                            placement: 'top',
                            highlight: 'rgb(170 255 128)',
                            mode: payoutEditableMode,
                            /**
                             * On success…
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
                                    element.bulkActions.removeClass('d-none');
                                } else {
                                    element.bulkActions.addClass('d-none');
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
     * @param valueField
     * @param {int|string} newValue
     * @private
     */
    const _refreshSrpAmountField = (valueField, newValue) => {
        console.log('New Value', newValue);
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
        valueField
            .attr('data-value', newValue)
            .addClass('srp-payout-amount-changed')
            .html(newValueFormatted);

        // Update fleet total SRP amount
        let totalSrpAmount = 0;
        const elementSrpAmount = $(
            '#table_aasrp_srp_requests .srp-request-status-approved .srp-payout-amount'
        );

        elementSrpAmount.each((i, payoutElement) => {
            totalSrpAmount += parseInt(payoutElement.getAttribute('data-value'));
        });

        console.log('Total SRP Amount', totalSrpAmount);

        console.log('Element Total Cost', element.totalSrpCost);

        element.totalSrpCost.html(numberFormatter({
            value: totalSrpAmount,
            locales: aaSrpSettings.locale,
            options: {
                style: 'currency',
                currency: 'ISK'
            }
        }));

        // Update copy to clipboard icon value
        const copyToClipboard = valueField.parent().parent().find('.copy-to-clipboard-icon i');
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

        console.log('ELEMENT TOTAL COST', element.totalSrpCost);

        // Update total_cost field in Database
        fetchPost({
            url: aaSrpSettings.url.updateTotalCost,
            csrfToken: aaSrpSettings.csrfToken,
            payload: {
                total_cost: totalSrpAmount
            },
            responseIsJson: true
        })
            .then((data) => {
                if (data.success === true) {
                    console.log('Total cost updated successfully:', data.message);

                    // Update fleet total SRP amount
                    element.totalSrpCost.html(numberFormatter({
                        value: totalSrpAmount,
                        locales: aaSrpSettings.locale,
                        options: {
                            style: 'currency',
                            currency: 'ISK'
                        }
                    }));
                } else {
                    console.error('Error updating total cost:', data.message);
                }
            })
            .catch((error) => {
                console.error('Error updating total cost:', error);
            });

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
                    const dt = element.srpRequestsTable.DataTable();

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

                            if (data.pending_requests >= 0) {
                                const target = $('a[href="/ship-replacement/"] + span.badge');

                                if (data.pending_requests === 0) {
                                    target.remove();
                                } else {
                                    target.text(data.pending_requests);
                                }

                                updateTotalNotificationsBadge();
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
                            srp_request_codes: checkedValues
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

                            element.bulkActions.addClass('d-none');
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
                            srp_request_codes: checkedValues
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

                            element.bulkActions.addClass('d-none');
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
     * Show info in game & copy ISK amount
     *
     * Copies the current payout amount (respecting inline edits) and asks ESI to
     * open the character's information window in the EVE client.
     * Deliberately does not reload the page or the table.
     */
    element.srpRequestsTable.on('click', 'button.srp-request-open-info', (event) => {
        event.preventDefault();

        const button = $(event.currentTarget);
        const row = button.closest('tr');
        const payoutAmount = parseInt(row.find('span.srp-payout-amount').attr('data-value')) || 0;
        const requestStatus = row.attr('class').match(/srp-request-status-(\w+)/);
        const translation = aaSrpSettings.translation.openCharacterInfo;

        const formattedAmount = numberFormatter({
            value: payoutAmount,
            locales: aaSrpSettings.locale,
            options: {
                style: 'currency',
                currency: 'ISK'
            }
        });

        // Copy first, while still inside the user's click
        const copyPromise = _copyToClipboard(String(payoutAmount));

        button.prop('disabled', true);

        const esiPromise = fetchPost({
            url: button.data('link'),
            csrfToken: aaSrpSettings.csrfToken,
            payload: {},
            responseIsJson: true
        }).catch((error) => {
            console.error(`Error: ${error.message}`);

            return {success: false, message: translation.requestFailed};
        });

        Promise.all([copyPromise, esiPromise]).then(([copied, response]) => {
            const messageParts = [];

            messageParts.push(
                copied
                    ? translation.copied.replace('#amount#', formattedAmount) // jshint ignore:line
                    : translation.notCopied
            );

            if (requestStatus && requestStatus[1] === 'rejected') {
                messageParts.push(translation.requestRejected);
            }

            messageParts.push(response.message);

            _showToast(messageParts.join(' · '), copied && response.success === true);
        }).finally(() => {
            button.prop('disabled', false);
        });
    });

    /**
     * Payout amount: Pressing Enter moves on to the next editable payout amount
     *
     * Only moves on once the form actually closes because of the submit, so it stays
     * put on validation or server errors. Unchanged values are skipped the same way.
     * The popover lives in `body`, and x-editable's `hidden` event doesn't bubble,
     * so neither can be delegated through the table.
     */
    $(document).on('keydown', '.editable-container form', (event) => {
        if (event.key !== 'Enter') {
            return;
        }

        const current = element.srpRequestsTable.find(`${editablePayoutSelector}.editable-open`);

        current
            .off('hidden.aasrpNextPayout')
            .one('hidden.aasrpNextPayout', (hiddenEvent, reason) => {
                if (reason === 'save' || reason === 'nochange') {
                    const editablePayouts = element.srpRequestsTable.find(editablePayoutSelector);

                    // Click, since x-editable only initializes an element on its first click
                    editablePayouts.eq(editablePayouts.index(current) + 1).trigger('click');
                }
            });
    });

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
            element.bulkActions.addClass('d-none');
        });
});
