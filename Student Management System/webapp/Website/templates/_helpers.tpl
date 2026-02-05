{{- define "Website.podName" -}}
{{- if eq . "app" -}}
web-api
{{- else if eq . "db" -}}
postgres-db
{{- else -}}
{{ . }}
{{- end -}}
{{- end -}}


{{- define "Website.hpaEnabled" -}}
{{- $hpaConfig := index .root.Values.hpa .name -}}
{{- if and $hpaConfig $hpaConfig.enabled -}}
true
{{- else -}}
false
{{- end -}}
{{- end -}}

