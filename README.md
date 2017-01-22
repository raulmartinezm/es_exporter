# Prometheus Elasticsearch exporter

Simple Prometheus exporter. Queries Elasticsearch and make the terms matches count available for Prometheus.

### Configuration

The fields and terms of matching are defined in config.json. Sample `config.json`:

```
{
  "name" : "freeradius_login_attempts",
  "help" : "Freeradius login attempts result",
  "fields" : {
    "login-ok": {
      "field": "login_result",
      "match": "OK"
    },
    "login-incorrect": {
    "field": "login_result",
    "match": "incorrect"
    }
  }
}
```

This example will query ES for matches of strings 'OK' and 'incorrect' in field 'login_result' and it will make
the result available for Prometheus as the metric `freeradius_login_attempts`. The labels of the metric are the
keys values in `fields` key.
