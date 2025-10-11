from typing import TypedDict
from langgraph.graph import START,END,StateGraph
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

gpt_llm= ChatOpenAI(model="gpt-4o-mini")

class Cricket(TypedDict):
    balls: int
    runs: int
    fours: int
    sixes: int
    strike_rate: float
    boundary_percentage: float
    summary: str


def strike_rate_calculator(state: Cricket ) -> Cricket:
    balls=state['balls']
    runs=state['runs']

    strike_rate= (runs/balls)*100
    state['strike_rate']=strike_rate

    return {"strike_rate":strike_rate}

def boundary_percentage_calculator(state: Cricket ) -> Cricket:
    runs=state['runs']
    fours=state['fours']
    sixes=state['sixes']

    boundary_percentage= (((fours*4)+(sixes*6))/runs)*100
    state['boundary_percentage']=boundary_percentage

    return {"boundary_percentage":boundary_percentage}

def summary_generator(state: Cricket ) -> Cricket:
    runs=state['runs']
    fours=state['fours']
    sixes=state['sixes']
    strike_rate=state['strike_rate']
    boundary_percentage=state['boundary_percentage']
    

    prompt=f"""Generate a 5 line summary for the score of the player in a game of cricket.
    runs:{runs}
    fours:{fours}
    sixes:{sixes}
    strike_rate:{strike_rate}
    boundary_percentage:{boundary_percentage}
    """

    summary=gpt_llm.invoke(prompt).content

    state['summary']=summary

    return state

graph =  StateGraph(Cricket)

graph.add_node("strike_rate_calculator",strike_rate_calculator)
graph.add_node("boundary_percentage_calculator",boundary_percentage_calculator)
graph.add_node("summary_generator",summary_generator)

graph.add_edge(START,"strike_rate_calculator")
graph.add_edge(START,"boundary_percentage_calculator")
graph.add_edge("strike_rate_calculator","summary_generator")
graph.add_edge("boundary_percentage_calculator","summary_generator")
graph.add_edge("summary_generator",END)

workflow=graph.compile()

init_state= {"balls":36, "runs":67, "fours":3, "sixes":5}

final_state=workflow.invoke(init_state)

print(final_state)