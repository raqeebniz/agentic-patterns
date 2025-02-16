from crewai.flow.flow import Flow, router, start, listen, or_ 
from litellm import completion


customer_email = (
    "Hi, I recently purchased a laptop from your store, but it has been malfunctioning. "
    "I am very disappointed with the quality and would like to know what can be done about it"
)

class Customer_support(Flow):
    API_KEY = "AIzaSyDHeCcuf5i6LZ5RMcIoh1YJdGx9r8arkHA"
    MODEL = "gemini/gemini-1.5-flash"
    """
    First LLM call: Extract the main issues from the customer's email.
    """
    @start()
    def extract_issues(self):
        response = completion(
            model=self.MODEL,
            api_key=self.API_KEY,
            messages=[
                {"role": "system", "content": "You are a customer support agent.your task is to extract the main issues from the customer's email."},
                {"role": "user", "content": f"Extract the main issues from the customer's email: {customer_email}"},
           ]
        )
        issue = response.choices[0].message.content.strip()
        self.state['issue'] = issue
        # print(f"Extracted issues: {issue}") 
        return issue
    
    @listen(extract_issues)
    def generate_response(self):
        """
        Second LLM call: Generate a response to the customer's email based on the main issues.
        """
        issue = self.state['issue']
        response = completion(
            model=self.MODEL,
            api_key=self.API_KEY,
            messages=[
                {"role": "system", "content": "You are a customer support agent.your task is to generate a response to the customer's email based on the main issues."},
                {"role": "user", "content": f"draft a reposnce adressing the following cutomer issue: {issue} ensure the reponse is clear ,professional and empathetic"},
            ]
        )
        generated_response = response.choices[0].message.content.strip()
        self.state['generated_response'] = generated_response
        # print(f"Generated response: {generated_response}")
        return generated_response
    
    @router(generate_response)
    def re_check_response(self):
        """
        Gate function to chek if the draft response include empathic language
        A simple chek would look for word like 'sorry' or 'apologize'
        """
        generated_response = self.state['generated_response']
        if "sorry" in generated_response.lower() or "apologize" in generated_response.lower():
            print("Response is empathic. Proceeding to next step.")
            return "sucess"
        else:
            print("Response is not empathic. Re-drafting response.")
            return "failure"
        
    @listen("failure")
    def re_generate_response(self):
        """
        3rd LLM call: Generate a final response to the customer's email.
        """
        generated_response = self.state.get('generated_response')
        response = completion(
            model=self.MODEL,
            api_key=self.API_KEY,
            messages=[
                {"role": "system", "content": "You are a customer support agent.your task is to generate a final response to the customer's email based on the main issues."},
                {"role": "user", "content": f"draft a final response adressing the following cutomer issue: {generated_response} rewrite it to better express the customer's concern"},
            ]
        )
        re_generated_response = response.choices[0].message.content.strip()
        self.state["final_response"] = re_generated_response
        # print(f"Re-generated response: {re_generated_response}")
        return re_generated_response

    @listen(or_("sucess", re_generate_response))
    def polish_response(self):
        """
        Fourth LLM call : Polish the response to make it more engaging and professional
        """
        response = self.state.get("final_response")
        response = completion(
            model=self.MODEL,
            api_key=self.API_KEY,
            messages=[
                {"role": "system", "content": "You are a customer support agent.your task is to polish the response to make it more engaging and professional."},
                {"role": "user", "content": f"polish the following response: {response} to make it more engaging and professional"},
            ]
        )
        polished_response = response.choices[0].message.content.strip()
        self.state['polished_response'] = polished_response
        print(f"Polished response: {polished_response}")
        return polished_response

    @listen("polish_response")
    def write_to_file(self):
        """
        Fifth LLm call : Write the polished response to file
        """
        polished_response = self.state['polished_response']
        with open("final_response.txt", "w") as file:
            file.write(polished_response)
        print("Response written to file: response.txt")
        return "Email_status: Responded"

def run():
    flow = Customer_support()
    flow.kickoff()

def plot():
    flow = Customer_support()
    flow.plot()


    
    
    
   
