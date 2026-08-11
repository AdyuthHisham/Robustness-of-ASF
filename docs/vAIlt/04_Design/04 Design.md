# 04 Design Map of Content

System architecture, interface definitions, and design decisions for the `kradar_visibility` pipeline and the noise-injection robust test-set work built on top of it.

## Notes

- [[Noise_Taxonomy|Noise Taxonomy]] — implemented corruption effects per modality, sourced papers, K-Radar's own pre-existing corruptions
- [[System_Architecture|System Architecture]] — module layout, data flow, error-handling strategy, web viewer design rationale
- [[API_Contracts|API Contracts]] — literal function signatures and I/O contracts, per module
- [[Output_Schema|Output Schema]] — the 44-column Parquet schema, field-by-field
