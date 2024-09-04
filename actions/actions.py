from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from inference import generate_code  # Import your model function
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
            dispatcher.utter_message(text="Device not found.")

        return []


class ActionSpecificDevice(Action):
    def name(self):
        return "action_on_specific_device"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[str, Any]) -> list[dict[str, Any]]:
        
        # entities = tracker.latest_message.get("entities", [])
        # print("entites:::", entities)
        # for entity in entities:
        #     print(f"Detected entity: {entity}")

        # Reset the slots you want to clear from previous turns
        reset_slots = [SlotSet("location", None), SlotSet("owner", None)]

        location = tracker.get_slot("location")
        owner = tracker.get_slot("owner")

        if location is not None:
            #print("Detected entity location: ", location)
            #generated_code = code

            dispatcher.utter_message(text=f"Found the light in the {location}...")
            # Get user message text
            user_message = tracker.latest_message.get('text')
            # Generate code using the model
            code = generate_code(user_message)
            # Send the generated code back to the user
            dispatcher.utter_message(text=f"Sure! The execution code is: \n```{code}```")
            location = location.replace(" ", "_")
            code = code.replace("location", location)
            #dispatcher.utter_message(text=f" Action excusion on device code: \n```{code}```")
            
            operation = code.split(".")[1]
            operation = operation.replace("on", "1")
            operation = operation.replace("off", "0")
            
            device = code.split(".")[0]
            #device_name = device.split("(")[1].split(",")[0]
            location = device.split("(")[1].split(",")[1]
            #print("******************location", location)
            #owner = device.split("(")[1].split(",")[2].split(')')[0]

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
            print(stderr.decode())


        if owner is not None:
            #print("Detected entity onwer: ", owner)
            dispatcher.utter_message(text=f"Found the light belongs to {owner}")
            # Get user message text
            user_message = tracker.latest_message.get('text')
            # Generate code using the model
            code = generate_code(user_message)
            # Send the generated code back to the user
            dispatcher.utter_message(text=f"Sure! The execution code is: \n```{code}```")

            owner = owner.replace("'s", "")
            code = code.replace("owner", owner)
            #print("*******owner**********", owner)
            #print("**************", code)
            #dispatcher.utter_message(text=f" Action excusion on device code: \n```{code}```")
            
            operation = code.split(".")[1]
            operation = operation.replace("on", "1")
            operation = operation.replace("off", "0")
            
            device = code.split(".")[0]
            device_name = device.split("(")[1].split(",")[0]
            #location = device.split("(")[1].split(",")[1]
            #print("******************location", location)
            owner = device.split("(")[1].split(",")[2].split(')')[0]

            rdf_graph = Graph()
            rdf_graph.parse("/home/zhou/Documents/rasa_chatbot/kg.ttl", format="turtle")
            query =  f"""
                    PREFIX : <http://example.com/ontology#>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                    PREFIX bot: <https://w3id.org/bot#> 
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

                    SELECT ?mac
                    WHERE {{
                    :{owner} :sitsIn ?room .
                    ?room bot:containsElement ?device .
                    ?device rdf:type :Light ;
                            :hasMacAddress ?mac .
                    }}
                    """
            
            # Execute the SPARQL query
            results = rdf_graph.query(query)
            print(results)
            # Extract the count from the query results
            for result in results:
                print(result)
                device_mac = result["mac"]

            print("**********************",device_mac)

            command = ['node', './wot/test.js', device_mac, operation]

            # Start the subprocess
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            print("Output:")
            print(stdout.decode())
            print(stderr.decode())
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
        dispatcher.utter_message(f"There are {num_devices} Philips Hue lamps detected, 1 in the IoT lab and 1 in the meeting room, which one would you like to turn on?".format(num_devices=result))
                # Get user message text
        user_message = tracker.latest_message.get('text')

        # Generate code using the model
        generated_code = generate_code(user_message)
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
        
        global code
        location = tracker.get_slot("location")
        owner = tracker.get_slot("owner")
        light = tracker.get_slot("light")

        print("********************", location)
        if location is not None:
            dispatcher.utter_message(text=f"Found the light in the {location}...")
            location = location.replace(" ", "_")
            code = code.replace("location", location)
            #dispatcher.utter_message(text=f" Action excusion on device code: \n```{code}```")
            
            operation = code.split(".")[1]
            operation = operation.replace("on", "1")
            operation = operation.replace("off", "0")
            
            device = code.split(".")[0]
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
            print(stderr.decode())

        # Send the generated code back to the user
        #dispatcher.utter_message(text=f"The execusion code is: \n```{generated_code}```")

        return []
    


class ActionTAPDevices(Action):

    def name(self) -> str:
        return "action_on_TAP_device"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict[str, Any]) -> list[dict[str, Any]]:

        location = tracker.get_slot("location")
        user_message = tracker.latest_message.get('text')
        code = generate_code(user_message)
        print("*******code*********", code)
        dispatcher.utter_message(text=f"Sure! The execution code is: \n```{code}```")
        #"Controller(streamdeck,location,owner).onEvent(buttonPress,1)=>Light(philipshue,IoT_lab,owner).writeProperty('power',on);"
        trigger = code.split("=>")[0]
        action = code.split("=>")[1]

        button_num = trigger.split(".onEvent(")[1].split(",")[1].split(")")[0]

        device = action.split(".")[0]
        operation = action.split(".")[1]
        operation = operation.replace("on", "1")
        operation = operation.replace("off", "0")

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

        command = ['node', './wot/tap.js', button_num, device_mac, operation]

        # Start the subprocess
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("Output:")
        print(stdout.decode())

        #print("Error:")
        print(stderr.decode())

        return []


