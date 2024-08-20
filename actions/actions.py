from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from infer import generate_code  # Import your model function
from typing import Any
from rasa_sdk.events import SlotSet
from rdflib import Graph, URIRef, Literal
from rdflib.plugins.sparql import prepareQuery
import subprocess

global code

class ActionExecute(Action):

    def name(self) -> str:
        return "action_execusion_on_device"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[str, Any]) -> list[dict[str, Any]]:
        # Check entities detected by Rasa
        entities = tracker.latest_message.get("entities", [])
        for entity in entities:
            print(f"Detected entity: {entity}")

        location = tracker.get_slot("location")
        owner = tracker.get_slot("owner")
        user_message = tracker.latest_message.get('text')


        global code
        #generated_code = code

        if location:
            dispatcher.utter_message(text=f"Found the light in the {location}...")
            location = location.replace(" ", "_")
            code = code.replace("location", location)
            dispatcher.utter_message(text=f" Action excusion on device code: \n```{code}```")
            
            # Light(philipshue,IoT_lab,None).writeProperty('power',on);

            device = code.split(".")[0]
            operation = code.split(".")[1]
            # operation = operation.replace("on", "1")
            # operation = operation.replace("off", "0")

            device_name = device.split("(")[1].split(",")[0]
            location = device.split("(")[1].split(",")[1]
            #print("******************location", location)
            owner = device.split("(")[1].split(",")[2].split(')')[0]

            rdf_graph = Graph()
            rdf_graph.parse("/home/zhou/Documents/rasa_chatbot/kg.ttl", format="turtle")
            query = f"""PREFIX : <http://example.com/ontology#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX bot: <https://w3id.org/bot#> 
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                    SELECT ?mac
                    WHERE {{
                        ?device rdf:type :Light .
                        :{location} bot:containsElement ?device .
                        ?device :hasMacAddress ?mac .
                    }}"""
            
            # Execute the SPARQL query
            results = rdf_graph.query(query)
            # Extract the count from the query results
            for result in results:
                device_mac = result["mac"]

            #print("**********************+",device_mac)

            command = ['node', './wot/test.js', device_mac, operation]

            # Start the subprocess
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print("Output:")
            print(stdout.decode())

            #print("Error:")
            print(stderr.decode())

        elif owner:
            dispatcher.utter_message(text=f"Okay, Turning on {owner}'s light.")
        else:
            dispatcher.utter_message(text="Turning on the specified light.")

        return []


class ActionSpecificDevice(Action):
    def name(self):
        return "action_on_specific_device"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[str, Any]) -> list[dict[str, Any]]:
        
        # Get user message text
        user_message = tracker.latest_message.get('text')

        # Generate code using the model
        generated_code = generate_code(user_message,"hues")

        # Send the generated code back to the user
        dispatcher.utter_message(text=f"Sure! Here's the code on specific device: \n```{generated_code}```")
        global code 
        code = generated_code
        return []


class ActionConnectedDevice(Action):
    def name(self):
        return "action_on_connected_device"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[str, Any]) -> list[dict[str, Any]]:
        
        # Get user message text
        user_message = tracker.latest_message.get('text')

        # Generate code using the model
        generated_code = generate_code(user_message, "sd_hue")

        # Send the generated code back to the user
        dispatcher.utter_message(text=f"Sure! Here's the code on specific device: \n```{generated_code}```")
        global code 
        code = generated_code
        return []


class SearchForSpecificDevice(Action):
    def name(self):
        return "action_search_for_number_of_devices_and_ask_which_one"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[str, Any]) -> list[dict[str, Any]]:
        # Check entities detected by Rasa
        entities = tracker.latest_message.get("entities", [])
        for entity in entities:
            print(f"Detected entity: {entity}")

        light = tracker.get_slot("light")
        #print(tracker.get_slot())
        rdf_graph = Graph()
        rdf_graph.parse("/home/zhou/Documents/rasa_chatbot/kg.ttl", format="turtle")  # Load RDF data
        print(light)
        # Example SPARQL query to count devices of type :Light
        query = """
        PREFIX : <http://example.com/ontology#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX bot: <https://w3id.org/bot#> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT (COUNT(?device) AS ?numDevices)
        WHERE {
            ?device rdf:type :Light
        }
        """

        # Execute the SPARQL query
        results = rdf_graph.query(query)

        # Extract the count from the query results
        for result in results:
            num_devices = result["numDevices"]
        print(result)

        # Example response to send back the number of devices found
        dispatcher.utter_message(f"Found {num_devices} devices of type 'Light', One Philips Hue lamp in the meeting room and one Philips Hue lamp in the IoT Lab.Which one do you want?".format(num_devices=result))
                # Get user message text
        user_message = tracker.latest_message.get('text')

        # Generate code using the model
        generated_code = generate_code(user_message, "hues")
        global code 
        code = generated_code
        #print("generated_code in first function: ", generated_code)
        return [SlotSet('generated_code', generated_code)]



class ActionGeneralDevice(Action):
    def name(self):
        return "action_on_general_device"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[str, Any]) -> list[dict[str, Any]]:
        
        # slots = tracker.slots
        # for slot_name, slot_value in slots.items():
        #     print(f"Slot name: {slot_name}, Slot value: {slot_value}")    


        # user_message = tracker.latest_message.get('text')
        # print("user message::", user_message)
        # # Generate code using the model
        # generated_code = tracker.get_slot('generated_code')
        # print("generated code is: ", generated_code)

        # # Check if the slot is set
        # if generated_code is None:
        #     dispatcher.utter_message(text="No generated code available.")
        #     return []

        # # Use the generated code
        # dispatcher.utter_message(text=f"this is the generated code from last step: \n```{generated_code}```")

        global code
        location = tracker.get_slot("location")
        owner = tracker.get_slot("owner")
        light = tracker.get_slot("light")

        if location is not None:
            generated_code = code.replace("location", location)
        if owner is not None:
            generated_code = code.replace("owner", owner)
        if light is not None:
            generated_code = code.replace("light", light)

        # Send the generated code back to the user
        dispatcher.utter_message(text=f"Action on general device code: \n```{generated_code}```")

        return []
    