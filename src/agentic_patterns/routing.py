from crewai.flow.flow import Flow, listen, router, or_, start
from litellm import completion


class Routing(Flow):
    API_KEY = "AIzaSyDHeCcuf5i6LZ5RMcIoh1YJdGx9r8arkHA"
    MODEL = "gemini/gemini-1.5-flash"
    """
    Routing based on user query  
    """
    @start()
    def customer_query(self):
        # get customer input from user
        customer_input = input("User input:")
        
        # save to flow state
        self.state["customer_query"] = customer_input

        return customer_input
    
    @router(customer_query)
    def routing(self):
        input = self.state["customer_query"]
        # Classify the user input in to a category
        response = completion(
            model = self.MODEL,
            api_key = self.API_KEY,
            messages = [
                {"role": "user", "content": f"here is the customer's query {input} \n\n Analyze the customer's query and determine the catogery it belongs to. If the query is releted to booking respond with 'booking'. If the query is releted to order respond with 'order'. If the query is releted to general information respond with 'general'."}
            ] 
        )
        # save the response to flow state
        response = response.choices[0].message.content.strip()
        self.state["routing_response"] = response
        if response == 'booking':
            return 'booking'
        elif response == 'order':
            return 'order'
        else:
            return 'general'
    
    
    @listen("booking")
    def booking_agent(self):
        print("Hello, I am the booking agent")
        return 'booking'
      
    @listen("order")
    def order_agent(self):
        print("hello, I am the order agent:")
        return 'order'
    
    @listen("general")
    def general_agent(self):
        print("Hello, I am general agent")
        return 'general'
    
    
def run():
    flow = Routing()
    flow.kickoff()

def plot():
    flow = Routing()
    flow.plot()



