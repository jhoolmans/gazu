import unittest
import requests_mock
import json

import gazu.client
import gazu.person

from utils import fakeid


class PersonTestCase(unittest.TestCase):
    def test_all(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons"),
                text=json.dumps([{"first_name": "John", "id": "person-01"}]),
            )
            persons = gazu.person.all_persons()
            person_instance = persons[0]
            self.assertEqual(person_instance["first_name"], "John")

    def test_get_person_by_full_name(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons"),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "id": "person-1",
                        },
                        {
                            "first_name": "Alex",
                            "last_name": "Doe",
                            "id": "person-2",
                        },
                        {
                            "first_name": "Ema",
                            "last_name": "Doe",
                            "id": "person-3",
                        },
                    ]
                ),
            )
            person = gazu.person.get_person_by_full_name("John Doe")
            self.assertEqual(person["id"], "person-1")
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons"),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "id": "person-01",
                        },
                        {
                            "first_name": "JohnDid",
                            "last_name": "",
                            "id": "person-2",
                        },
                        {
                            "first_name": "Ema",
                            "last_name": "Doe",
                            "id": "person-3",
                        },
                    ]
                ),
            )
            person = gazu.person.get_person_by_full_name("JohnDid")
            self.assertEqual(person["id"], "person-2")
            self.assertEqual(
                gazu.person.get_person_by_full_name("Unknown"), None
            )

    def test_get_person_by_desktop_login(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/persons?desktop_login=john.doe"
                ),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "desktop_login": "john.doe",
                            "id": "person-01",
                        }
                    ]
                ),
            )
            person = gazu.person.get_person_by_desktop_login("john.doe")
            self.assertEqual(person["id"], "person-01")

    def test_get_person_by_email(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons?email=john@gmail.com"),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "desktop_login": "john.doe",
                            "id": "person-01",
                        }
                    ]
                ),
            )
            person = gazu.person.get_person_by_email("john@gmail.com")
            self.assertEqual(person["id"], "person-01")

    def test_new_person(self):
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons?email=john@gmail.com"),
                text=json.dumps([]),
            )
            mock.post(
                gazu.client.get_full_url("data/persons/new"),
                text=json.dumps(
                    [
                        {
                            "first_name": "John",
                            "last_name": "Doe",
                            "email": "john@gmail.com",
                            "desktop_login": "john.doe",
                            "phone": "06 07 07 07 07",
                            "role": "user",
                            "id": "person-01",
                        }
                    ]
                ),
            )
            gazu.person.new_person(
                "Jhon", "Doe", "john@gmail.com", "+33 6 07 07 07 07", "user"
            )

    def test_all_organisations(self):
        result = [{"id": fakeid("organisation-1"), "name": "organisation-1"}]
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/organisations"),
                text=json.dumps(result),
            )
            self.assertEqual(gazu.person.all_organisations(), result)

    def test_get_person(self):
        result = {"id": fakeid("John Doe"), "full_name": "John Doe"}
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url(
                    "data/persons/%s" % (fakeid("John Doe"))
                ),
                text=json.dumps(result),
            )
            self.assertEqual(
                gazu.person.get_person(fakeid("John Doe")), result
            )

    def test_get_person_url(self):
        wanted_result = "%s/people/%s/" % (
            gazu.client.get_api_url_from_host(),
            fakeid("person-1"),
        )
        self.assertEqual(
            wanted_result, gazu.person.get_person_url(fakeid("person-1"))
        )

    def test_get_organisation(self):
        with requests_mock.mock() as mock:
            result = {"organisation": "test-organisation"}
            mock.get(
                gazu.client.get_full_url("auth/authenticated"),
                text=json.dumps(result),
            )
            self.assertEqual(
                gazu.person.get_organisation(), "test-organisation"
            )

    def test_get_presence_log(self):
        result = """
        2021;1;2;3;4;5;6;7;8;9;10;11;12;13;14;15;16;17;18;19;20;21;22;23;24;25;26;27;28;29;30;31
        Super Admin;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"""
        with requests_mock.mock() as mock:
            mock.get(
                gazu.client.get_full_url("data/persons/presence-logs/2021-08"),
                text=result,
            )
            self.assertEqual(gazu.person.get_presence_log("2021", "8"), result)

    def test_set_avatar(self):
        with requests_mock.mock() as mock:
            path = "/pictures/thumbnails/persons/%s" % fakeid("person-1")
            mock.post(
                gazu.client.get_full_url(path),
                text=json.dumps(
                    {"id": fakeid("person-1"), "name": "test-name"}
                ),
            )
            person_id = gazu.person.set_avatar(
                fakeid("person-1"), "./tests/fixtures/v1.png"
            )

            self.assertEqual(person_id["id"], fakeid("person-1"))
