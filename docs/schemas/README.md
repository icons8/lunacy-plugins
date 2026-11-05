# Automation API v2 request schemas

These 26 JSON Schemas describe the preview build's direct HTTP request parser contracts. They use JSON Schema Draft 2020-12 and were checked against source-generated Automation API DTO metadata on 2026-11-05. Each filename matches `POST /v2/<filename-without-.schema.json>`; `get_session` also supports GET.

Start with the [human API reference](../API_V2_REFERENCE.md) and [worked workflows](../AUTOMATION_WORKFLOWS.md). A schema accepts structure, not permissions, target state, reference ownership, revisions, graph validity or work budgets. Runtime rules are documented in the reference and advertised by `/v2/get_session`.

These are HTTP bodies, without grouped MCP/AI Chat wrappers. Model selectors are the closed union `{"id":"..."}` or `{"clientRef":"..."}`. Free-form FREE values still need native validation; an object accepted by the schema is not necessarily a supported patch.

| Area | Schemas |
| --- | --- |
| Session and discovery | [get_session](get_session.schema.json), [list_documents](list_documents.schema.json), [list_pages](list_pages.schema.json), [query_design_system](query_design_system.schema.json), [get_design_system_assets](get_design_system_assets.schema.json), [get_asset_usage](get_asset_usage.schema.json), [get_design_context](get_design_context.schema.json), [get_request_status](get_request_status.schema.json), [get_automation_documentation](get_automation_documentation.schema.json). |
| Mutations | [apply_component_changes](apply_component_changes.schema.json), [apply_style_changes](apply_style_changes.schema.json), [apply_variable_changes](apply_variable_changes.schema.json), [manage_pages](manage_pages.schema.json). |
| Navigation and lifecycle | [activate_document](activate_document.schema.json), [activate_page](activate_page.schema.json), [create_document](create_document.schema.json), [open_document](open_document.schema.json), [rename_document](rename_document.schema.json), [reorder_tabs](reorder_tabs.schema.json), [save_document](save_document.schema.json), [close_document](close_document.schema.json). |
| Libraries | [list_libraries](list_libraries.schema.json), [connect_library](connect_library.schema.json), [disconnect_library](disconnect_library.schema.json), [import_library_assets](import_library_assets.schema.json), [refresh_libraries](refresh_libraries.schema.json). |

Availability is build-specific. A missing `/v2/get_session` cannot establish support in that installed application. Read the reference's FREE compatibility note before mixing saved-document fragments with API types.
