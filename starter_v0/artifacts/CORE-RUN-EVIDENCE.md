# Core run evidence

Generated from saved live run JSON. See BASELINE-IMPROVEMENTS.md for interpretation.

## v0

Run: [JSON](evidence/v0_B_base_openrouter_20260915T182614315954.json)

Model: `openrouter/openai/gpt-4o-mini`; artifact: `v0+p233ec2cecfdf+teb3e2243f237`

```json
{
  "total_cases": 30,
  "measured_cases": 30,
  "provider_error_cases": 0,
  "passed_cases": 21,
  "case_accuracy": 0.7,
  "tool_routing_accuracy": 0.7667,
  "argument_accuracy": 0.7,
  "multiturn_accuracy": 0.8,
  "failure_counts": {
    "wrong_tool": 3,
    "missing_info": 3,
    "wrong_boundary": 3
  },
  "observed_mismatch_counts": {
    "extra_tool_call": 2,
    "missing_tool_call": 5,
    "wrong_arg_value": 2
  }
}
```

New passes: baseline

Regressions: none

| Case | Grade | Mismatch | Tool result review |
|---|---|---|---|
| H01_service_status_routing | PASS | none | check_service_status: degraded |
| H02_device_routing | PASS | none | inspect_device: returned data |
| H03_kb_routing | PASS | none | search_kb: returned data; 1 search results |
| H04_user_routing | FAIL | extra tool call inspect_device | lookup_user: returned data; inspect_device: asset_not_found |
| H05_device_check_arg | PASS | none | inspect_device: returned data |
| H06_environment_arg | PASS | none | check_service_status: maintenance |
| H07_format_report | PASS | none | format_incident_report: returned data |
| H08_out_of_scope | PASS | none | No tool; inspect actual_text in JSON |
| H09_meta_no_tool | PASS | none | No tool; inspect actual_text in JSON |
| H10_missing_asset | FAIL | missing tool call clarify; extra tool call inspect_device | inspect_device: asset_not_found |
| H11_missing_employee | FAIL | missing tool call clarify; extra tool call lookup_user | lookup_user: employee_not_found |
| H12_confirm_before_ticket | FAIL | missing tool call clarify; extra tool call create_ticket | create_ticket: created |
| H13_parallel_status_and_device | FAIL | check: expected 'vpn', got None | check_service_status: degraded; inspect_device: returned data |
| H14_out_of_scope_coding | PASS | none | No tool; inspect actual_text in JSON |
| M01_clarify_then_asset | PASS | none | inspect_device: returned data |
| M02_carry_environment | PASS | none | check_service_status: maintenance |
| M03_correct_asset | PASS | none | inspect_device: returned data |
| M04_correct_employee | PASS | none | lookup_user: returned data |
| M05_ticket_confirmation | FAIL | extra tool call create_ticket | create_ticket: needs_confirmation; clarify: returned data; awaiting user |
| M06_switch_tool | PASS | none | search_kb: returned data; 1 search results |
| H15_compare_environments | PASS | none | check_service_status: operational; check_service_status: maintenance |
| H16_compare_two_assets | PASS | none | inspect_device: returned data; inspect_device: returned data |
| H17_triage_with_three_sources | FAIL | check: expected 'vpn', got 'all' | inspect_device: returned data; check_service_status: degraded; search_kb: returned data; 2 search results |
| H18_user_and_asset | PASS | none | lookup_user: returned data; inspect_device: returned data |
| H19_ambiguous_environment | FAIL | missing tool call clarify; extra tool call check_service_status | check_service_status: maintenance |
| H20_format_without_refetch | PASS | none | format_incident_report: returned data |
| M07_cancel_previous_action | PASS | none | No tool; inspect actual_text in JSON |
| M08_correct_then_parallel | PASS | none | inspect_device: returned data; check_service_status: degraded |
| M09_confirmation_invalidated | FAIL | missing tool call clarify; extra tool call create_ticket | create_ticket: created |
| M10_latest_intent_wins | PASS | none | lookup_user: returned data |

### Failed call traces

#### H04_user_routing

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "lookup_user",
        "args": {
          "employee_id": "EMP-1003"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "lookup_user",
      "args": {
        "employee_id": "EMP-1003"
      }
    },
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "EMP-1003"
      }
    }
  ]
}
```

#### H10_missing_asset

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "text"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "laptop",
        "check": "network"
      }
    }
  ]
}
```

#### H11_missing_employee

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "text"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "lookup_user",
      "args": {
        "employee_id": "Sales"
      }
    }
  ]
}
```

#### H12_confirm_before_ticket

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "yes_no"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "create_ticket",
      "args": {
        "summary": "Lỗi VPN trên LT-204",
        "priority": "high",
        "asset_id": "LT-204",
        "confirmed": true
      }
    }
  ]
}
```

#### H13_parallel_status_and_device

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "check_service_status",
        "args": {
          "service": "vpn",
          "environment": "production"
        }
      },
      {
        "name": "inspect_device",
        "args": {
          "asset_id": "LT-204",
          "check": "vpn"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "check_service_status",
      "args": {
        "service": "vpn",
        "environment": "production"
      }
    },
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "LT-204"
      }
    }
  ]
}
```

#### M05_ticket_confirmation

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "yes_no"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "create_ticket",
      "args": {
        "summary": "Lỗi VPN LT-204",
        "priority": "high"
      }
    },
    {
      "name": "clarify",
      "args": {
        "question": "Bạn có xác nhận muốn tạo ticket với thông tin sau không? \n- Tóm tắt: Lỗi VPN LT-204 \n- Mức ưu tiên: High",
        "response_type": "yes_no"
      }
    }
  ]
}
```

#### H17_triage_with_three_sources

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "inspect_device",
        "args": {
          "asset_id": "LT-318",
          "check": "vpn"
        }
      },
      {
        "name": "check_service_status",
        "args": {
          "service": "vpn",
          "environment": "production"
        }
      },
      {
        "name": "search_kb",
        "args": {
          "category": "vpn"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "LT-318",
        "check": "all"
      }
    },
    {
      "name": "check_service_status",
      "args": {
        "service": "vpn",
        "environment": "production"
      }
    },
    {
      "name": "search_kb",
      "args": {
        "query": "VPN macOS",
        "category": "vpn"
      }
    }
  ]
}
```

#### H19_ambiguous_environment

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "choice",
          "options": [
            "production",
            "staging"
          ]
        }
      }
    ]
  },
  "actual": [
    {
      "name": "check_service_status",
      "args": {
        "service": "email",
        "environment": "staging"
      }
    }
  ]
}
```

#### M09_confirmation_invalidated

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "yes_no"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "create_ticket",
      "args": {
        "summary": "Lỗi Wi-Fi LT-240, nghi mất dữ liệu.",
        "priority": "critical",
        "confirmed": true
      }
    }
  ]
}
```

## v1

Run: [JSON](evidence/v1_B_base_openrouter_20260915T182736789483.json)

Model: `openrouter/openai/gpt-4o-mini`; artifact: `v1+p88cbf71f0873+teb3e2243f237`

```json
{
  "total_cases": 30,
  "measured_cases": 30,
  "provider_error_cases": 0,
  "passed_cases": 23,
  "case_accuracy": 0.7667,
  "tool_routing_accuracy": 0.8667,
  "argument_accuracy": 0.7667,
  "multiturn_accuracy": 1.0,
  "failure_counts": {
    "wrong_tool": 3,
    "missing_info": 3,
    "wrong_boundary": 1
  },
  "observed_mismatch_counts": {
    "extra_tool_call": 1,
    "missing_tool_call": 3,
    "wrong_arg_value": 3
  }
}
```

New passes: M05_ticket_confirmation, M09_confirmation_invalidated

Regressions: none

| Case | Grade | Mismatch | Tool result review |
|---|---|---|---|
| H01_service_status_routing | PASS | none | check_service_status: degraded |
| H02_device_routing | PASS | none | inspect_device: returned data |
| H03_kb_routing | PASS | none | search_kb: returned data; 1 search results |
| H04_user_routing | FAIL | extra tool call inspect_device | lookup_user: returned data; inspect_device: asset_not_found |
| H05_device_check_arg | PASS | none | inspect_device: returned data |
| H06_environment_arg | PASS | none | check_service_status: maintenance |
| H07_format_report | PASS | none | format_incident_report: returned data |
| H08_out_of_scope | PASS | none | No tool; inspect actual_text in JSON |
| H09_meta_no_tool | PASS | none | No tool; inspect actual_text in JSON |
| H10_missing_asset | FAIL | missing tool call clarify; extra tool call inspect_device | inspect_device: asset_not_found |
| H11_missing_employee | FAIL | missing tool call clarify; extra tool call lookup_user | lookup_user: employee_not_found |
| H12_confirm_before_ticket | FAIL | response_type: expected 'yes_no', got 'text' | clarify: returned data; awaiting user |
| H13_parallel_status_and_device | FAIL | check: expected 'vpn', got None | check_service_status: degraded; inspect_device: returned data |
| H14_out_of_scope_coding | PASS | none | No tool; inspect actual_text in JSON |
| M01_clarify_then_asset | PASS | none | inspect_device: returned data |
| M02_carry_environment | PASS | none | check_service_status: maintenance |
| M03_correct_asset | PASS | none | inspect_device: returned data |
| M04_correct_employee | PASS | none | lookup_user: returned data |
| M05_ticket_confirmation | PASS | none | clarify: returned data; awaiting user |
| M06_switch_tool | PASS | none | search_kb: returned data; 1 search results |
| H15_compare_environments | PASS | none | check_service_status: operational; check_service_status: maintenance |
| H16_compare_two_assets | PASS | none | inspect_device: returned data; inspect_device: returned data |
| H17_triage_with_three_sources | FAIL | check: expected 'vpn', got None | inspect_device: returned data; check_service_status: degraded; search_kb: returned data; 2 search results |
| H18_user_and_asset | PASS | none | lookup_user: returned data; inspect_device: returned data |
| H19_ambiguous_environment | FAIL | missing tool call clarify; extra tool call check_service_status | check_service_status: maintenance |
| H20_format_without_refetch | PASS | none | format_incident_report: returned data |
| M07_cancel_previous_action | PASS | none | No tool; inspect actual_text in JSON |
| M08_correct_then_parallel | PASS | none | inspect_device: returned data; check_service_status: degraded |
| M09_confirmation_invalidated | PASS | none | clarify: returned data; awaiting user |
| M10_latest_intent_wins | PASS | none | lookup_user: returned data |

### Failed call traces

#### H04_user_routing

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "lookup_user",
        "args": {
          "employee_id": "EMP-1003"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "lookup_user",
      "args": {
        "employee_id": "EMP-1003"
      }
    },
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "EMP-1003"
      }
    }
  ]
}
```

#### H10_missing_asset

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "text"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "laptop",
        "check": "network"
      }
    }
  ]
}
```

#### H11_missing_employee

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "text"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "lookup_user",
      "args": {
        "employee_id": "Sales"
      }
    }
  ]
}
```

#### H12_confirm_before_ticket

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "yes_no"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "clarify",
      "args": {
        "question": "Tóm tắt sự cố cho ticket là gì?",
        "response_type": "text"
      }
    }
  ]
}
```

#### H13_parallel_status_and_device

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "check_service_status",
        "args": {
          "service": "vpn",
          "environment": "production"
        }
      },
      {
        "name": "inspect_device",
        "args": {
          "asset_id": "LT-204",
          "check": "vpn"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "check_service_status",
      "args": {
        "service": "vpn",
        "environment": "production"
      }
    },
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "LT-204"
      }
    }
  ]
}
```

#### H17_triage_with_three_sources

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "inspect_device",
        "args": {
          "asset_id": "LT-318",
          "check": "vpn"
        }
      },
      {
        "name": "check_service_status",
        "args": {
          "service": "vpn",
          "environment": "production"
        }
      },
      {
        "name": "search_kb",
        "args": {
          "category": "vpn"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "LT-318"
      }
    },
    {
      "name": "check_service_status",
      "args": {
        "service": "vpn",
        "environment": "production"
      }
    },
    {
      "name": "search_kb",
      "args": {
        "query": "VPN macOS",
        "category": "vpn"
      }
    }
  ]
}
```

#### H19_ambiguous_environment

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "choice",
          "options": [
            "production",
            "staging"
          ]
        }
      }
    ]
  },
  "actual": [
    {
      "name": "check_service_status",
      "args": {
        "service": "email",
        "environment": "staging"
      }
    }
  ]
}
```

## v2

Run: [JSON](evidence/v2_B_base_openrouter_20260915T183422429231.json)

Model: `openrouter/openai/gpt-4o-mini`; artifact: `v2+p88cbf71f0873+t258f2f862f37`

```json
{
  "total_cases": 30,
  "measured_cases": 30,
  "provider_error_cases": 0,
  "passed_cases": 27,
  "case_accuracy": 0.9,
  "tool_routing_accuracy": 0.9667,
  "argument_accuracy": 0.9,
  "multiturn_accuracy": 1.0,
  "failure_counts": {
    "wrong_tool": 2,
    "missing_info": 1
  },
  "observed_mismatch_counts": {
    "wrong_arg_value": 2,
    "missing_tool_call": 1
  }
}
```

New passes: H04_user_routing, H10_missing_asset, H11_missing_employee, H12_confirm_before_ticket

Regressions: none

| Case | Grade | Mismatch | Tool result review |
|---|---|---|---|
| H01_service_status_routing | PASS | none | check_service_status: degraded |
| H02_device_routing | PASS | none | inspect_device: returned data |
| H03_kb_routing | PASS | none | search_kb: returned data; 1 search results |
| H04_user_routing | PASS | none | lookup_user: returned data |
| H05_device_check_arg | PASS | none | inspect_device: returned data |
| H06_environment_arg | PASS | none | check_service_status: maintenance |
| H07_format_report | PASS | none | format_incident_report: returned data |
| H08_out_of_scope | PASS | none | No tool; inspect actual_text in JSON |
| H09_meta_no_tool | PASS | none | No tool; inspect actual_text in JSON |
| H10_missing_asset | PASS | none | clarify: returned data; awaiting user |
| H11_missing_employee | PASS | none | clarify: returned data; awaiting user |
| H12_confirm_before_ticket | PASS | none | clarify: returned data; awaiting user |
| H13_parallel_status_and_device | FAIL | check: expected 'vpn', got None | check_service_status: degraded; inspect_device: returned data |
| H14_out_of_scope_coding | PASS | none | No tool; inspect actual_text in JSON |
| M01_clarify_then_asset | PASS | none | inspect_device: returned data |
| M02_carry_environment | PASS | none | check_service_status: maintenance |
| M03_correct_asset | PASS | none | inspect_device: returned data |
| M04_correct_employee | PASS | none | lookup_user: returned data |
| M05_ticket_confirmation | PASS | none | clarify: returned data; awaiting user |
| M06_switch_tool | PASS | none | search_kb: returned data; 1 search results |
| H15_compare_environments | PASS | none | check_service_status: operational; check_service_status: maintenance |
| H16_compare_two_assets | PASS | none | inspect_device: returned data; inspect_device: returned data |
| H17_triage_with_three_sources | FAIL | check: expected 'vpn', got 'all' | inspect_device: returned data; check_service_status: degraded; search_kb: returned data; 2 search results |
| H18_user_and_asset | PASS | none | lookup_user: returned data; inspect_device: returned data |
| H19_ambiguous_environment | FAIL | missing tool call clarify; extra tool call check_service_status | check_service_status: maintenance |
| H20_format_without_refetch | PASS | none | format_incident_report: returned data |
| M07_cancel_previous_action | PASS | none | No tool; inspect actual_text in JSON |
| M08_correct_then_parallel | PASS | none | inspect_device: returned data; check_service_status: degraded |
| M09_confirmation_invalidated | PASS | none | clarify: returned data; awaiting user |
| M10_latest_intent_wins | PASS | none | lookup_user: returned data |

### Failed call traces

#### H13_parallel_status_and_device

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "check_service_status",
        "args": {
          "service": "vpn",
          "environment": "production"
        }
      },
      {
        "name": "inspect_device",
        "args": {
          "asset_id": "LT-204",
          "check": "vpn"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "check_service_status",
      "args": {
        "service": "vpn",
        "environment": "production"
      }
    },
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "LT-204"
      }
    }
  ]
}
```

#### H17_triage_with_three_sources

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "inspect_device",
        "args": {
          "asset_id": "LT-318",
          "check": "vpn"
        }
      },
      {
        "name": "check_service_status",
        "args": {
          "service": "vpn",
          "environment": "production"
        }
      },
      {
        "name": "search_kb",
        "args": {
          "category": "vpn"
        }
      }
    ]
  },
  "actual": [
    {
      "name": "inspect_device",
      "args": {
        "asset_id": "LT-318",
        "check": "all"
      }
    },
    {
      "name": "check_service_status",
      "args": {
        "service": "vpn",
        "environment": "production"
      }
    },
    {
      "name": "search_kb",
      "args": {
        "query": "VPN macOS",
        "category": "vpn"
      }
    }
  ]
}
```

#### H19_ambiguous_environment

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "choice",
          "options": [
            "production",
            "staging"
          ]
        }
      }
    ]
  },
  "actual": [
    {
      "name": "check_service_status",
      "args": {
        "service": "email",
        "environment": "staging"
      }
    }
  ]
}
```

## v3

Run: [JSON](evidence/v3_B_base_openrouter_20260915T183622303623.json)

Model: `openrouter/openai/gpt-4o-mini`; artifact: `v3+p88cbf71f0873+t2d2e0fe2c35f`

```json
{
  "total_cases": 30,
  "measured_cases": 30,
  "provider_error_cases": 0,
  "passed_cases": 29,
  "case_accuracy": 0.9667,
  "tool_routing_accuracy": 0.9667,
  "argument_accuracy": 0.9667,
  "multiturn_accuracy": 1.0,
  "failure_counts": {
    "missing_info": 1
  },
  "observed_mismatch_counts": {
    "missing_tool_call": 1
  }
}
```

New passes: H13_parallel_status_and_device, H17_triage_with_three_sources

Regressions: none

| Case | Grade | Mismatch | Tool result review |
|---|---|---|---|
| H01_service_status_routing | PASS | none | check_service_status: degraded |
| H02_device_routing | PASS | none | inspect_device: returned data |
| H03_kb_routing | PASS | none | search_kb: returned data; 1 search results |
| H04_user_routing | PASS | none | lookup_user: returned data |
| H05_device_check_arg | PASS | none | inspect_device: returned data |
| H06_environment_arg | PASS | none | check_service_status: maintenance |
| H07_format_report | PASS | none | format_incident_report: returned data |
| H08_out_of_scope | PASS | none | No tool; inspect actual_text in JSON |
| H09_meta_no_tool | PASS | none | No tool; inspect actual_text in JSON |
| H10_missing_asset | PASS | none | clarify: returned data; awaiting user |
| H11_missing_employee | PASS | none | clarify: returned data; awaiting user |
| H12_confirm_before_ticket | PASS | none | clarify: returned data; awaiting user |
| H13_parallel_status_and_device | PASS | none | check_service_status: degraded; inspect_device: returned data |
| H14_out_of_scope_coding | PASS | none | No tool; inspect actual_text in JSON |
| M01_clarify_then_asset | PASS | none | inspect_device: returned data |
| M02_carry_environment | PASS | none | check_service_status: maintenance |
| M03_correct_asset | PASS | none | inspect_device: returned data |
| M04_correct_employee | PASS | none | lookup_user: returned data |
| M05_ticket_confirmation | PASS | none | clarify: returned data; awaiting user |
| M06_switch_tool | PASS | none | search_kb: returned data; 1 search results |
| H15_compare_environments | PASS | none | check_service_status: operational; check_service_status: maintenance |
| H16_compare_two_assets | PASS | none | inspect_device: returned data; inspect_device: returned data |
| H17_triage_with_three_sources | PASS | none | inspect_device: returned data; check_service_status: degraded; search_kb: returned data; 2 search results |
| H18_user_and_asset | PASS | none | lookup_user: returned data; inspect_device: returned data |
| H19_ambiguous_environment | FAIL | missing tool call clarify; extra tool call check_service_status | check_service_status: maintenance |
| H20_format_without_refetch | PASS | none | format_incident_report: returned data |
| M07_cancel_previous_action | PASS | none | No tool; inspect actual_text in JSON |
| M08_correct_then_parallel | PASS | none | inspect_device: returned data; check_service_status: degraded |
| M09_confirmation_invalidated | PASS | none | clarify: returned data; awaiting user |
| M10_latest_intent_wins | PASS | none | lookup_user: returned data |

### Failed call traces

#### H19_ambiguous_environment

```json
{
  "expected": {
    "tool_calls": [
      {
        "name": "clarify",
        "args": {
          "response_type": "choice",
          "options": [
            "production",
            "staging"
          ]
        }
      }
    ]
  },
  "actual": [
    {
      "name": "check_service_status",
      "args": {
        "service": "email",
        "environment": "staging"
      }
    }
  ]
}
```

