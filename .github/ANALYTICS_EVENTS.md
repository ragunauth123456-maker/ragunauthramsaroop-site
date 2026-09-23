# RR Free Tools engagement measurement

GA4 measurement ID: G-28FHYG7T0G.

The site records event names and non-sensitive page/tool identifiers only:

- tool_started
- tool_completed
- result_copied
- result_printed
- tool_shared
- template_downloaded
- white_paper_opened
- topic_opened
- profile_opened
- feedback_opened
- report_downloaded

Never add tool input values, resume text, grievance content, stakeholder names, contact details or other visitor-entered data to analytics parameters.

Analytics storage defaults to denied under Google Consent Mode. Advertising storage, advertising user data and ad personalisation remain denied.


## Decision-support events added 23 September 2026

- tool_started
- tool_completed
- result_chart_rendered
- result_copied
- result_printed
- export_clicked
- report_exported, report_type only
- scenario_save_clicked
- scenario_saved, has_result only
- scenario_restore_clicked
- scenario_restored
- scenario_compare_clicked
- scenario_compared, scenario_count only
- scenario_shared, share_method only
- scenario_link_loaded
- preset_applied, preset_name only
- csv_imported, row_count only
- csv_template_downloaded
- tool_shared, share_method only
- related_tool_opened
- methodology_opened
- language_changed, language only
- embed_previewed, tool_slug only
- embed_code_copied
- toolkit_exported
- toolkit_cleared
- tool_feedback, rating only
- tool_feedback_note_saved, note_length only
- tool_directory_search, query_length only

Privacy rule: analytics must never receive entered tool values, pasted text, saved scenario contents, feedback-note contents, names, email addresses, or uploaded CSV content.
- web_vital, metric_name and numeric metric_value only. LCP, CLS and INP are measured in supported browsers after analytics consent.
