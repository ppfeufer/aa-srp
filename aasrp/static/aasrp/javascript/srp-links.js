/* global _bootstrapTooltip, moment, aaSrpSettings, fetchGet, numberFormatter, _removeSearchFromColumnControl, DataTable */

$(document).ready(() => {
    'use strict';

    const elementTableSrpLinks = $('#table_tab-srp-links');

    console.log('aaSrpSettings:', aaSrpSettings);

    /**
     * Table: SRP Links
     */
    let totalSrpAmount = 0;

    fetchGet({url: aaSrpSettings.url.availableSrpLinks})
        .then((data) => {
            if (data) {
                const dt = new DataTable(elementTableSrpLinks, { // eslint-disable-line no-unused-vars
                    language: aaSrpSettings.dataTables.language,
                    data: data,
                    layout: aaSrpSettings.dataTables.layout,
                    ordering: aaSrpSettings.dataTables.ordering,
                    columnControl: aaSrpSettings.dataTables.columnControl,
                    paging: aaSrpSettings.dataTables.paging,
                    columns: [
                        {
                            data: 'srp_name',
                            className: 'srp-link-fleet-name'
                        },
                        {
                            data: 'creator',
                            className: 'srp-link-creator'
                        },
                        {
                            data: {
                                display: (data) => data.fleet_time === null ? '' : moment(data.fleet_time).utc().format(aaSrpSettings.datetimeFormat),
                                sort: (data) => data.fleet_time === null ? '' : data.fleet_time

                            },
                            className: 'srp-link-fleet-time'
                        },
                        {
                            data: 'fleet_type',
                            className: 'srp-link-fleet-type'
                        },
                        // {
                        //     data: 'fleet_commander',
                        //     className: 'srp-link-fleet-commander'
                        // },
                        {
                            data: 'fleet_doctrine',
                            className: 'srp-link-fleet-doctrine'
                        },
                        {
                            data: 'aar_link',
                            className: 'srp-link-aar-link'
                        },
                        {
                            data: 'srp_code',
                            render: {
                                display: 'display',
                                filter: 'sort',
                                sort: 'sort'
                            },
                            className: 'srp-link-code'
                        },
                        {
                            data: {
                                display: (data) => numberFormatter({
                                    value: data.srp_costs,
                                    locales: aaSrpSettings.locale,
                                    options: {
                                        style: 'currency',
                                        currency: 'ISK'
                                    }
                                }),
                                filter: (data) => data.srp_costs,
                                sort: (data) => data.srp_costs
                            },
                            className: 'srp-link-total-cost text-end'
                        },
                        {
                            data: 'srp_status',
                            className: 'srp-link-status'
                        },
                        {
                            data: 'pending_requests',
                            className: 'srp-link-pending-requests text-end'
                        },
                        {
                            data: 'actions',
                            className: 'srp-link-actions text-end'
                        }
                    ],
                    columnDefs: [
                        {
                            targets: [2, 5, 7, 9],
                            columnControl: _removeSearchFromColumnControl(aaSrpSettings.dataTables.columnControl, 1)
                        },
                        {
                            target: 10,
                            orderable: false,
                            width: 115,
                            columnControl: [
                                {target: 0, content: []},
                                {target: 1, content: []}
                            ]
                        }
                    ],
                    order: [[2, 'asc']],
                    /**
                     * When ever a row is created …
                     *
                     * @param row
                     * @param data
                     * @param rowIndex
                     */
                    createdRow: (row, data, rowIndex) => {
                        // Row id attr
                        $(row)
                            .attr('data-row-id', rowIndex)
                            .attr('data-srp-code', data.srp_code.sort);

                        totalSrpAmount += parseInt(data.srp_costs);

                        $('.srp-dashboard-total-isk-cost-amount').html(
                            numberFormatter({
                                value: totalSrpAmount,
                                locales: aaSrpSettings.locale,
                                options: {
                                    style: 'currency',
                                    currency: 'ISK'
                                }
                            })
                        );
                    },
                    initComplete: () => {
                        const dt = elementTableSrpLinks.DataTable();

                        // Initialize Bootstrap tooltips
                        _bootstrapTooltip({selector: '#table_tab-srp-links'});

                        // Re-initialize tooltips on each draw
                        dt.on('draw', () => {
                            _bootstrapTooltip({selector: '#table_tab-srp-links'});
                        });
                    }
                });
            }
        })
        .catch((error) => {
            console.error('Error fetching SRP links:', error);
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
