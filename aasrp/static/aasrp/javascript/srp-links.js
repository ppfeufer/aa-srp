/* global _bootstrapTooltip, aaSrpSettings, numberFormatter, _removeSearchFromColumnControl, DataTable */

$(document).ready(() => {
    'use strict';

    const elementTableSrpLinks = $('#table_tab-srp-links');

    /**
     * Format the Total Cost column in the DataTable to display currency values.
     *
     * @param {Object} dt - The DataTable instance.
     * @returns {void}
     * @private
     */
    const _formatTotalCostColumn = (dt) => {
        dt.rows().every((rowIdx) => {
            const rowData = dt.row(rowIdx).data();
            const formattedCost = numberFormatter({
                value: rowData[7],
                locales: aaSrpSettings.locale,
                options: {
                    style: 'currency',
                    currency: 'ISK'
                }
            });

            dt.cell(rowIdx, 7).data(formattedCost);
        });
    };

    // Initialize DataTable options
    let dataTableOptions = {
        ...aaSrpSettings.dataTables,
        order: [[2, 'asc']],
        columnDefs: [
            // Remove column control search from these columns
            {
                targets: [
                    2, // Fleet Time
                    5 // AAR Link
                ],
                columnControl: _removeSearchFromColumnControl(aaSrpSettings.dataTables.columnControl, 1)
            },
            // Remove column control from these columns completely and make them non-orderable
            {
                targets: [
                    7, // Total Cost
                    9 // Pending Requests
                ],
                columnControl: [
                    {target: 0, content: []},
                    {target: 1, content: []}
                ]
            },
            // Make these columns non-orderable
            {
                targets: [
                    5, // AAR Link
                    7, // Total Cost
                    9 // Pending Requests
                ],
                orderable: false
            },
            // Column definitions for specific columns
            {
                target: 7,
                className: 'srp-link-total-cost',
                type: 'num'
            },
            {
                target: 9,
                className: 'srp-link-pending-requests'
            },
            {
                target: 10,
                className: 'srp-link-actions text-end'
            }
        ],
        initComplete: () => {
            const dt = elementTableSrpLinks.DataTable();

            _bootstrapTooltip({selector: '#table_tab-srp-links'});
            _formatTotalCostColumn(dt);

            dt.on('draw', () => {
                _bootstrapTooltip({selector: '#table_tab-srp-links'});
                _formatTotalCostColumn(dt);
            });

            $('input[name="srp-requests-filter"]').on('change', () => dt.draw());
        }
    };

    if (aaSrpSettings.paging === false) {
        dataTableOptions = {
            ...dataTableOptions,
            pageLength: 99999,
            layout: { // See: https://datatables.net/reference/option/layout
                topStart: null,
                bottomEnd: null
            }
        };
    }

    // Initialize DataTable
    const dt = new DataTable(elementTableSrpLinks, dataTableOptions);
    dt.on('preXhr.dt', (e, settings, data) => {
        data['filter[has_requests]'] = $('#aasrp-srp-request-filter-pending').is(':checked');
    });

    /**
     * Modals
     */
    const modalEnableSrpLink = $('#enable-srp-link');
    const modalDisableSrpLink = $('#disable-srp-link');
    const modalDeleteSrpLink = $('#delete-srp-link');

    // Enable link modal
    modalEnableSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalEnableSrpLink.find('#modal-button-confirm-enable-srp-link')
            .attr('href', url);
        modalEnableSrpLink.find('.modal-body').html(`${aaSrpSettings.translation.modal.enableSrpLink.body}<p class="fw-bold">${name}</p>`);
    }).on('hide.bs.modal', () => {
        modalEnableSrpLink.find('.modal-body').html('');
    });

    // Disable link modal
    modalDisableSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalDisableSrpLink.find('#modal-button-confirm-disable-srp-link')
            .attr('href', url);
        modalDisableSrpLink.find('.modal-body').html(`${aaSrpSettings.translation.modal.disableSrpLink.body}<p class="fw-bold">${name}</p>`);
    }).on('hide.bs.modal', () => {
        modalDisableSrpLink.find('.modal-body').html('');
    });

    // Delete link modal
    modalDeleteSrpLink.on('show.bs.modal', (event) => {
        const button = $(event.relatedTarget);
        const url = button.data('url');
        const name = button.data('name');

        modalDeleteSrpLink.find('#modal-button-confirm-delete-srp-link').attr('href', url);
        modalDeleteSrpLink.find('.modal-body').html(`${aaSrpSettings.translation.modal.deleteSrpLink.body}<p class="fw-bold">${name}</p>`);
    }).on('hide.bs.modal', () => {
        modalDeleteSrpLink.find('.modal-body').html('');
    });
});
