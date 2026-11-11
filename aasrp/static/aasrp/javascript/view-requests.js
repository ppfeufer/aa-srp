/* global _bootstrapTooltip, _copyToClipboard, _formatCurrency, _removeSearchFromColumnControl, _showToast, aaSrpSettings, DataTable, fetchGet, fetchPost, moment */

$(document).ready(() => {
    'use strict';

    const element = {
        srpRequestsTable: $('#table_aasrp_srp_requests'),
        bulkActions: $('div.card-srp-request-bulk-actions'),
        totalSrpCost: $('#srp-fleet-total-cost'),
        pendingSrpCost: $('#srp-fleet-pending-cost')
    };
    const editablePayoutSelector = '.srp-request-payout-amount-editable .srp-payout-amount';

    // Set initial total SRP cost value
    element.totalSrpCost.html(_formatCurrency(element.totalSrpCost.data('total-srp-cost') || 0));
    element.pendingSrpCost.html(_formatCurrency(element.pendingSrpCost.data('pending-srp-cost') || 0));

    // Set fleet time in overview header
    const fleetTimeElement = $('#srp-fleet-time');
    const fleetTime = fleetTimeElement.data('fleet-time');

    if (fleetTime) {
        fleetTimeElement.html(moment(fleetTime).utc().format(aaSrpSettings.datetimeFormat));
    }

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

    const payoutEditableMode = aaSrpSettings.payoutEditableMode || 'popup';

    // DataTable column indices for easier reference
    const dtColumn = {
        requestTime: 0,
        requester: 1,
        character: 2,
        ship: 3,
        iskLoss: 4,
        srpPayout: 5,
        additionalInfo: 6,
        status: 7,
        actions: 8,
        bulkActionsCheckbox: 9,
        requestCode: 10, // Invisible: Request Code (for internal use, not displayed to users)
        requestStatus: 11 // Invisible: Request Status (for internal use, not displayed to users)
    };

    const columnDefs = [
        {
            targets: [
                dtColumn.requestTime,
                dtColumn.iskLoss,
                dtColumn.srpPayout
            ],
            columnControl: _removeSearchFromColumnControl(
                aaSrpSettings.dataTables.columnControl,
                1
            )
        },
        // Remove column control from these columns completely
        {
            targets: [
                dtColumn.status,
                dtColumn.actions,
                dtColumn.bulkActionsCheckbox
            ],
            columnControl: [
                {target: 0, content: []},
                {target: 1, content: []}
            ]
        },
        // Make these columns non-orderable
        {
            targets: [
                dtColumn.status,
                dtColumn.actions,
                dtColumn.bulkActionsCheckbox
            ],
            orderable: false
        },
        // Hidden columns
        {
            targets: [
                dtColumn.requestCode,
                dtColumn.requestStatus
            ],
            visible: false
        },
        // Request time column
        {
            target: dtColumn.requestTime,
            render: (data) => moment(data).utc().format(aaSrpSettings.datetimeFormat),
            className: 'srp-request-time'
        },
        // Requester column
        {
            target: dtColumn.requester,
            className: 'srp-request-requester'
        },
        // Character column
        {
            target: dtColumn.character,
            className: 'srp-request-character'
        },
        // Ship column
        {
            target: dtColumn.ship,
            className: 'srp-request-ship'
        },
        // ISK lost column
        {
            target: dtColumn.iskLoss,
            render: (data) => _formatCurrency(data),
            className: 'srp-request-zkb-loss-amount',
            type: 'num'
        },
        // SRP payout column
        {
            target: dtColumn.srpPayout,
            render: (data) => {
                const ctcIcon = `<sup class="copy-to-clipboard-icon"><i class="copy-to-clipboard fa-regular fa-copy ms-2 cursor-pointer" data-clipboard-text="${data}" data-bs-tooltip="aa-srp" aria-label="${aaSrpSettings.translation.copyPayoutAmountToClipboard}" title="${aaSrpSettings.translation.copyPayoutAmountToClipboard}"></i></sup>`;
                const html = `<span class="srp-payout d-flex justify-content-end align-items-baseline"><span class="srp-payout-tooltip"><span class="srp-payout-amount">#payout_amount_localized#</span></span>${ctcIcon}</span>`;
                return html.replace(
                    '#payout_amount_localized#',
                    _formatCurrency(data)
                );
            },
            className: 'srp-request-payout',
            type: 'num',
            ...(payoutEditableMode === 'inline' ? {width: 325} : {})
        },
        // Additional Info column
        {
            target: dtColumn.additionalInfo,
            className: 'srp-request-additional-info'
        },
        // Status column
        {
            target: dtColumn.status,
            className: 'srp-request-status text-center'
        },
        // Actions column
        {
            target: dtColumn.actions,
            className: 'srp-request-actions text-end',
            width: 120
        },
        // Bulk action checkbox column
        {
            target: dtColumn.bulkActionsCheckbox,
            className: 'srp-request-bulk-actions-checkbox text-end'
        }
    ];

    /**
     * Table :: SRP Requests
     *
     * @type {*|jQuery}
     */
    const dt = new DataTable(element.srpRequestsTable, {
        ...aaSrpSettings.dataTables,
        ajax: {
            url: aaSrpSettings.url.requestsForSrpLink,
            error: (xhr, error) => console.error('Error fetching data:', xhr, error)
        },
        columnDefs: columnDefs,
        order: [dtColumn.requestTime, 'asc'],
        /**
         * When ever a row is created…
         *
         * @param row
         * @param data
         * @param rowIndex
         */
        createdRow: (row, data, rowIndex) => {
            const srpRequestCode = data[dtColumn.requestCode];
            const srpRequestStatus = data[dtColumn.requestStatus].toLowerCase();
            const srpRequestPayoutAmount = data[dtColumn.srpPayout] === 0 ? null : data[dtColumn.srpPayout];

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

            $('input[name="srp-request-status-filter"]').on('change', () => dt.draw());

            // Show bootstrap tooltips
            _bootstrapTooltip({selector: '#table_aasrp_srp_requests'});

            dt.on('draw', () => {
                _bootstrapTooltip({selector: '#table_aasrp_srp_requests'});
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
                 * This needs to be exactly as it is, otherwise the number
                 * formatter will not work correctly after the edit.
                 *
                 * @returns {boolean}
                 */
                display: () => false,
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
    dt.on('preXhr.dt', (e, settings, data) => {
        data['filter[request_status]'] = $('input[name="srp-request-status-filter"]:checked').val();
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
        newValue = parseInt(newValue);

        // Update payout value formatted
        // const newValueFormatted = `${new Intl.NumberFormat(aaSrpSettings.locale).format(newValue)} ISK`;
        const newValueFormatted = _formatCurrency(newValue);

        // Update the element
        valueField
            .attr('data-value', newValue === 0 ? null : newValue)
            .addClass('srp-payout-amount-changed')
            .html(newValueFormatted);

        // Update fleet total SRP amount
        let totalSrpAmount = 0;
        let pendingSrpAmount = 0;

        const elementSrpPayoutAmount = {
            approved: $('#table_aasrp_srp_requests .srp-request-status-approved .srp-payout-amount'),
            pending: $('#table_aasrp_srp_requests .srp-request-status-pending .srp-payout-amount'),
            rejected: $('#table_aasrp_srp_requests .srp-request-status-rejected .srp-payout-amount')
        };

        elementSrpPayoutAmount.approved.each((i, payoutElement) => {
            totalSrpAmount += parseInt(payoutElement.getAttribute('data-value') || 0);
        });
        elementSrpPayoutAmount.pending.each((i, payoutElement) => {
            pendingSrpAmount += parseInt(payoutElement.getAttribute('data-value') || 0);
        });

        element.totalSrpCost.html(_formatCurrency(totalSrpAmount));
        element.pendingSrpCost.html(_formatCurrency(pendingSrpAmount));

        // Update copy to clipboard icon value
        const copyToClipboard = valueField.parent().parent().find('.copy-to-clipboard-icon i');
        copyToClipboard.attr('data-clipboard-text', newValue);
    };

    /**
     * Helper function: Reloading SRP calculation in our DataTable
     *
     * @param {object} summary Fleet-wide request counts and payout totals
     * @private
     */
    const _reloadSrpCalculations = (summary) => {
        const totalSrpAmount = summary.totalSrpAmount;
        const pendingSrpAmount = summary.pendingSrpAmount;

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
                    // Update fleet total SRP amount
                    element.totalSrpCost.html(_formatCurrency(totalSrpAmount));
                    // Update fleet pending SRP amount
                    element.pendingSrpCost.html(_formatCurrency(pendingSrpAmount));
                } else {
                    console.error('Error updating total cost:', data.message);
                }
            })
            .catch((error) => {
                console.error('Error updating total cost:', error);
            });

        // Update requests counts
        $('.srp-requests-total-count').html(summary.requestsTotal);
        $('.srp-requests-pending-count').html(summary.requestsPending);
        $('.srp-requests-approved-count').html(summary.requestsApproved);
        $('.srp-requests-rejected-count').html(summary.requestsRejected);
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
            element.srpRequestsTable.DataTable().ajax.reload((response) => {
                _reloadSrpCalculations(response.summary);
            });

            if (data.pending_requests >= 0) {
                const target = $(`a[href="${aaSrpSettings.url.base}"] + span.badge`);

                if (data.pending_requests === 0) {
                    target.remove();
                } else {
                    target.text(data.pending_requests);
                }

                updateTotalNotificationsBadge();
            }
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
        const formattedAmount = _formatCurrency(payoutAmount);

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
