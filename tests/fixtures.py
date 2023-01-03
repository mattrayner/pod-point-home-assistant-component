"""Data fixtures used within tests."""
POD_MINIMAL_FIXTURE = {
    "id": 12234,
    "name": None,
    "ppid": "PSL-123456",
    "payg": False,
    "home": True,
    "public": False,
    "evZone": False,
    "address_id": 1234,
    "description": "",
    "commissioned_at": "2022-01-25T09:00:00+00:00",
    "created_at": "2022-02-13T10:39:05+00:00",
    "last_contact_at": "2022-02-15T11:18:56+00:00",
    "contactless_enabled": False,
    "unit_id": 123456,
    "timezone": "UTC",
    "model": {
        "id": 123,
        "name": "S7-UC-03-ACA",
        "vendor": "Pod Point",
        "supports_payg": False,
        "supports_ocpp": False,
        "supports_contactless": False,
        "image_url": None,
    },
    "price": None,
    "statuses": [],
}

POD_COMPLETE_FIXTURE = {
    "id": 12234,
    "name": None,
    "ppid": "PSL-123456",
    "payg": False,
    "home": True,
    "public": False,
    "evZone": False,
    "location": {"lat": 0.12345, "lng": 2.45678901},
    "address_id": 1234,
    "description": "",
    "commissioned_at": "2022-01-25T09:00:00+00:00",
    "created_at": "2022-02-13T10:39:05+00:00",
    "last_contact_at": "2022-02-15T11:18:56+00:00",
    "contactless_enabled": False,
    "unit_id": 123456,
    "timezone": "UTC",
    "model": {
        "id": 123,
        "name": "S7-UC-03-ACA",
        "vendor": "Pod Point",
        "supports_payg": False,
        "supports_ocpp": False,
        "supports_contactless": False,
        "image_url": None,
    },
    "price": None,
    "statuses": [
        {
            "id": 2,
            "name": "Charging",
            "key_name": "charging",
            "label": "Charging",
            "door": "A",
            "door_id": 1,
        }
    ],
    "unit_connectors": [
        {
            "connector": {
                "id": 123,
                "door": "A",
                "door_id": 1,
                "power": 7,
                "current": 32,
                "voltage": 230,
                "charge_method": "Single Phase AC",
                "has_cable": False,
                "socket": {
                    "type": "IEC 62196-2 Type 2",
                    "description": "Type 2 socket",
                    "ocpp_name": "sType2",
                    "ocpp_code": 3,
                },
            }
        }
    ],
    "charge_schedules": [
        {
            "uid": "24b342c8-8cbb-11ec-1111-0a9268fc07a0",
            "start_day": 1,
            "start_time": "06:00:00",
            "end_day": 2,
            "end_time": "00:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24b8aeac-8cbb-11ec-2222-0a9268fc07a0",
            "start_day": 2,
            "start_time": "02:00:00",
            "end_day": 2,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24bb6606-8cbb-11ec-3333-0a9268fc07a0",
            "start_day": 3,
            "start_time": "02:00:00",
            "end_day": 3,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24be0168-8cbb-11ec-4444-0a9268fc07a0",
            "start_day": 4,
            "start_time": "02:00:00",
            "end_day": 4,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24c089b0-8cbb-11ec-5555-0a9268fc07a0",
            "start_day": 5,
            "start_time": "02:00:00",
            "end_day": 5,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24c346aa-8cbb-11ec-6666-0a9268fc07a0",
            "start_day": 6,
            "start_time": "02:00:00",
            "end_day": 6,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24c6bf10-8cbb-11ec-7777-0a9268fc07a0",
            "start_day": 7,
            "start_time": "02:00:00",
            "end_day": 7,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
    ],
}

POD_COMPREHENSIVE_FIXTURE = {
    "id": 12234,
    "name": None,
    "ppid": "PSL-123456",
    "payg": False,
    "home": True,
    "public": False,
    "evZone": False,
    "location": {"lat": 0.12345, "lng": 2.45678901},
    "address_id": 1234,
    "description": "",
    "commissioned_at": "2022-01-25T09:00:00+00:00",
    "created_at": "2022-02-13T10:39:05+00:00",
    "last_contact_at": "2022-02-15T11:18:56+00:00",
    "contactless_enabled": False,
    "unit_id": 123456,
    "timezone": "UTC",
    "model": {
        "id": 123,
        "name": "S7-UC-03-ACA",
        "vendor": "Pod Point",
        "supports_payg": False,
        "supports_ocpp": False,
        "supports_contactless": False,
        "image_url": None,
    },
    "price": None,
    "statuses": [
        {
            "id": 2,
            "name": "Charging",
            "key_name": "charging",
            "label": "Charging",
            "door": "A",
            "door_id": 1,
        },
        {
            "id": 1,
            "name": "Available",
            "key_name": "available",
            "label": "Available",
            "door": "B",
            "door_id": 2,
        },
    ],
    "unit_connectors": [
        {
            "connector": {
                "id": 123,
                "door": "A",
                "door_id": 1,
                "power": 7,
                "current": 32,
                "voltage": 230,
                "charge_method": "Single Phase AC",
                "has_cable": False,
                "socket": {
                    "type": "IEC 62196-2 Type 2",
                    "description": "Type 2 socket",
                    "ocpp_name": "sType2",
                    "ocpp_code": 3,
                },
            }
        },
        {
            "connector": {
                "id": 234,
                "door": "B",
                "door_id": 2,
                "power": 7,
                "current": 32,
                "voltage": 230,
                "charge_method": "Single Phase AC",
                "has_cable": False,
                "socket": {
                    "type": "IEC 62196-2 Type 2",
                    "description": "Type 2 socket",
                    "ocpp_name": "sType2",
                    "ocpp_code": 3,
                },
            }
        },
    ],
    "charge_schedules": [
        {
            "uid": "24b342c8-8cbb-11ec-1111-0a9268fc07a0",
            "start_day": 1,
            "start_time": "06:00:00",
            "end_day": 2,
            "end_time": "00:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24b8aeac-8cbb-11ec-2222-0a9268fc07a0",
            "start_day": 2,
            "start_time": "02:00:00",
            "end_day": 2,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24bb6606-8cbb-11ec-3333-0a9268fc07a0",
            "start_day": 3,
            "start_time": "02:00:00",
            "end_day": 3,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24be0168-8cbb-11ec-4444-0a9268fc07a0",
            "start_day": 4,
            "start_time": "02:00:00",
            "end_day": 4,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24c089b0-8cbb-11ec-5555-0a9268fc07a0",
            "start_day": 5,
            "start_time": "02:00:00",
            "end_day": 5,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24c346aa-8cbb-11ec-6666-0a9268fc07a0",
            "start_day": 6,
            "start_time": "02:00:00",
            "end_day": 6,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
        {
            "uid": "24c6bf10-8cbb-11ec-7777-0a9268fc07a0",
            "start_day": 7,
            "start_time": "02:00:00",
            "end_day": 7,
            "end_time": "07:00:00",
            "status": {"is_active": False},
        },
    ],
}

CHARGES_COMPLETE_FIXTURE = {
    "charges": [
        {
            "id": 1,
            "kwh_used": 3.2,
            "duration": 0,
            "starts_at": "2022-03-08:00:00+00:00",
            "ends_at": None,
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 0,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 2,
            "kwh_used": 6.3,
            "duration": 1393,
            "starts_at": "2022-03-10T13:00:00+00:00",
            "ends_at": "2022-03-11T12:00:00+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 116,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 3,
            "kwh_used": 2.1,
            "duration": 932,
            "starts_at": "2022-03-08T17:26:04+00:00",
            "ends_at": "2022-03-09T08:58:10+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 39,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 4,
            "kwh_used": 9.2,
            "duration": 163,
            "starts_at": "2022-03-08T14:00:26+00:00",
            "ends_at": "2022-03-08T16:43:26+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 169,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 5,
            "kwh_used": 8.2,
            "duration": 3969,
            "starts_at": "2022-03-05T17:26:32+00:00",
            "ends_at": "2022-03-08T11:35:58+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 150,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 6,
            "kwh_used": 1.8,
            "duration": 171,
            "starts_at": "2022-02-27T08:40:05+00:00",
            "ends_at": "2022-02-27T11:31:50+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 33,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 7,
            "kwh_used": 0.5,
            "duration": 1097,
            "starts_at": "2022-02-25T17:31:52+00:00",
            "ends_at": "2022-02-26T11:49:40+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 9,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 8,
            "kwh_used": 0.6,
            "duration": 5,
            "starts_at": "2022-02-25T17:25:49+00:00",
            "ends_at": "2022-02-25T17:31:28+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 11,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 9,
            "kwh_used": 0.4,
            "duration": 4,
            "starts_at": "2022-02-25T17:21:01+00:00",
            "ends_at": "2022-02-25T17:25:41+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 123456},
            "energy_cost": 7,
            "organisation": {"id": None, "name": None},
        },
        {
            "id": 10,
            "kwh_used": 5.2,
            "duration": 336,
            "starts_at": "2022-02-25T11:17:04+00:00",
            "ends_at": "2022-02-25T16:53:53+00:00",
            "billing_event": {
                "id": None,
                "amount": None,
                "currency": None,
                "exchange_rate": 0,
                "presentment_amount": None,
                "presentment_currency": None,
            },
            "location": {
                "id": 1234,
                "home": True,
                "address": {"id": 1234, "business_name": ""},
                "timezone": "Europe/London",
            },
            "pod": {"id": 12234},
            "energy_cost": 95,
            "organisation": {"id": None, "name": None},
        },
    ]
}

FIRMWARE_COMPLETE_FIXTURE = {
    "data": [
        {
            "serial_number": "123456789",
            "version_info": {
                "manifest_id": "A30P-3.1.22-00001"
            },
            "update_status": {
                "is_update_available": False
            }
        }
    ]
}

USER_COMPLETE_FIXTURE = {
    "users": {
        "id": 123456,
        "email": "podpoint@example.com",
        "first_name": "Example",
        "last_name": "User",
        "role": "user",
        "hasHomeCharge": 1,
        "locale": "en",
        "preferences": [
            {
                "unitOfDistance": "mi"
            }
        ],
        "account": {
            "user_id": 123456,
            "uid": "1a756c9b-dfac-4c2a-ba13-9cdcc2399366",
            "balance": 173,
            "currency": "GBP",
            "billing_address": {
                "business_name": "",
                "address1": "",
                "address2": "",
                "town": "",
                "postcode": "",
                "country": ""
            },
            "phone": "",
            "mobile": None
        },
        "vehicle": {
            "id": 129,
            "uuid": "citroenC5AircrossPlugInHybrid",
            "name": "C5 Aircross Plug-in Hybrid",
            "capacity": 7,
            "batteryCapacity": 13.2,
            "startYear": None,
            "endYear": None,
            "image": {
                "@1x": "https://pod-point-admin-images-prod.imgix.net/vehicle-model-images/8eb13aeaf566eaedbe648bab8a5c14c0.png?w=0.5&h=0.5",
                "@2x": "https://pod-point-admin-images-prod.imgix.net/vehicle-model-images/8eb13aeaf566eaedbe648bab8a5c14c0.png?w=0.75&h=0.75",
                "@3x": "https://pod-point-admin-images-prod.imgix.net/vehicle-model-images/8eb13aeaf566eaedbe648bab8a5c14c0.png"
            },
            "make": {
                "id": 22,
                "name": "Citroen",
                "logo": {
                    "@1x": "https://pod-point-admin-images-prod.imgix.net/vehicle-make-logos/315261a80a1287b6d1b70f5c0fa8ccde.png?w=0.5&h=0.5",
                    "@2x": "https://pod-point-admin-images-prod.imgix.net/vehicle-make-logos/315261a80a1287b6d1b70f5c0fa8ccde.png?w=0.75&h=0.75",
                    "@3x": "https://pod-point-admin-images-prod.imgix.net/vehicle-make-logos/315261a80a1287b6d1b70f5c0fa8ccde.png"
                }
            }
        },
        "unit": {
            "id": 123456,
            "ppid": "211092",
            "name": None,
            "status": "Available",
            "architecture": "soloArch3",
            "pod": {
                "id": 123456,
                "name": None,
                "ppid": "PSL-211092",
                "payg": False,
                "home": True,
                "public": False,
                "evZone": False,
                "location": {
                    "lat": 23.543643,
                    "lng": 7.2434543
                },
                "address_id": 12345,
                "description": "",
                "commissioned_at": "2022-01-25T09:00:00+00:00",
                "created_at": "2022-02-13T10:39:05+00:00",
                "last_contact_at": "2023-01-10T19:17:12+00:00",
                "contactless_enabled": False,
                "unit_id": 123456,
                "timezone": "UTC",
                "model": {
                    "id": 256,
                    "name": "S7-UC-03-ACA",
                    "vendor": "Pod Point",
                    "supports_payg": False,
                    "supports_ocpp": False,
                    "supports_contactless": False,
                    "image_url": None
                },
                "statuses": [
                    {
                        "id": 1,
                        "name": "Available",
                        "key_name": "available",
                        "label": "Available",
                        "door": "A",
                        "door_id": 1
                    }
                ],
                "unit_connectors": [
                    {
                        "connector": {
                            "id": 303,
                            "door": "A",
                            "door_id": 1,
                            "power": 7,
                            "current": 32,
                            "voltage": 230,
                            "charge_method": "Single Phase AC",
                            "has_cable": False,
                            "socket": {
                                "type": "IEC 62196-2 Type 2",
                                "description": "Type 2 socket",
                                "ocpp_name": "sType2",
                                "ocpp_code": 3
                            }
                        }
                    }
                ],
                "charge_schedules": [
                    {
                        "uid": "2e47721e-cdb2-49d7-ba47-f956975b7ed5",
                        "start_day": 1,
                        "start_time": "00:00:00",
                        "end_day": 1,
                        "end_time": "00:00:01",
                        "status": {
                            "is_active": False
                        }
                    },
                    {
                        "uid": "bf3188eb-745e-4fbd-baa9-8a141eb708ed",
                        "start_day": 2,
                        "start_time": "00:00:00",
                        "end_day": 2,
                        "end_time": "00:00:01",
                        "status": {
                            "is_active": False
                        }
                    },
                    {
                        "uid": "80eeba4b-2e69-4e04-a1e9-6e7dfc88528e",
                        "start_day": 3,
                        "start_time": "00:00:00",
                        "end_day": 3,
                        "end_time": "00:00:01",
                        "status": {
                            "is_active": False
                        }
                    },
                    {
                        "uid": "3fddde7d-0809-43b3-8d16-64faf8a84e97",
                        "start_day": 4,
                        "start_time": "00:00:00",
                        "end_day": 4,
                        "end_time": "00:00:01",
                        "status": {
                            "is_active": False
                        }
                    },
                    {
                        "uid": "79e69a06-2c3a-442b-a65f-5766140d8874",
                        "start_day": 5,
                        "start_time": "00:00:00",
                        "end_day": 5,
                        "end_time": "00:00:01",
                        "status": {
                            "is_active": False
                        }
                    },
                    {
                        "uid": "0d2e6fdc-2a3d-4808-84e1-22e1d9d10be8",
                        "start_day": 6,
                        "start_time": "00:00:00",
                        "end_day": 6,
                        "end_time": "00:00:01",
                        "status": {
                            "is_active": False
                        }
                    },
                    {
                        "uid": "f79028be-00e9-4a86-a6c4-d474b7aaab37",
                        "start_day": 7,
                        "start_time": "00:00:00",
                        "end_day": 7,
                        "end_time": "00:00:01",
                        "status": {
                            "is_active": False
                        }
                    }
                ]
            }
        }
    }
}
