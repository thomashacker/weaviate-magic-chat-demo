from st_weaviate_connection import WeaviateConnection
import streamlit as st
import time
import sys
import os

from dotenv import load_dotenv

# Constants
ENV_VARS = ["WEAVIATE_URL", "WEAVIATE_API_KEY", "OPENAI_API_KEY"]
NUM_IMAGES_PER_ROW = 3


# Functions
def get_env_vars(env_vars: list) -> dict:
    """Retrieve environment variables
    @parameter env_vars : list - List containing keys of environment variables
    @returns dict - A dictionary of environment variables
    """
    load_dotenv()

    env_vars = {}
    for var in ENV_VARS:
        value = os.environ.get(var, "")
        if value == "":
            st.error(f"{var} not set", icon="🚨")
            sys.exit(f"{var} not set")
        env_vars[var] = value

    return env_vars


def display_chat_messages() -> None:
    """Print message history
    @returns None
    """
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "images" in message:
                for i in range(0, len(message["images"]), NUM_IMAGES_PER_ROW):
                    cols = st.columns(NUM_IMAGES_PER_ROW)
                    for j in range(NUM_IMAGES_PER_ROW):
                        if i + j < len(message["images"]):
                            cols[j].image(message["images"][i + j], width=200)


# Environment variables
env_vars = get_env_vars(ENV_VARS)
url = env_vars["WEAVIATE_URL"]
api_key = env_vars["WEAVIATE_API_KEY"]
openai_key = env_vars["OPENAI_API_KEY"]

# Check keys
if url == "" or api_key == "" or openai_key == "":
    st.error(f"Environment variables not set", icon="🚨")
    sys.exit("Environment variables not set")

# Title
st.title("🔮 Magic Chat")

# Connection to Weaviate thorugh Connector
conn = st.experimental_connection(
    "weaviate",
    type=WeaviateConnection,
    url=os.getenv("WEAVIATE_URL"),
    api_key=os.getenv("WEAVIATE_API_KEY"),
    additional_headers={"X-OpenAI-Api-Key": openai_key},
)

with st.sidebar:
    st.title("🔮 Magic Chat")
    st.subheader("The Generative Gathering")
    st.markdown(
        """Magic Chat is a chatbot built with [Streamlit](https://streamlit.io/) and [Weaviate](https://weaviate.io/) to search for [Magic the Gathering](https://magic.wizards.com/en) cards. 
        It offers multiple search options such as traditional BM25, Semantic, Hybrid, and Generative Search to find cards for your dream deck. 
        Whether you're looking for blue cards to nullify spells, black cards to create an undead army, or just want to find new cool cards! 
        Our Weaviate database contains 27k cards from the [Scryfall API](https://scryfall.com/) ready for you to be discovered."""
    )
    st.header("Settings")
    st.success("Connected to Weaviate client", icon="💚")

# Search Mode descriptions

bm25_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, bm25: {{ query: "{input}" }}) 
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

vector_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, nearText: {{ concepts: ["{input}"] }}) 
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

hybrid_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, hybrid: {{ query: "{input}" alpha:0.5 }}) 
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

generative_gql = """
        {{
            Get {{
                Card(limit: {limit_card}, nearText: {{ concepts: ["{input}"] }})
                {{
                    name
                    card_id
                    img
                    mana_cost
                    type
                    mana_produced
                    power
                    toughness
                    color
                    keyword
                    set
                    rarity
                    description
                    _additional {{
                        generate(
                            groupedResult: {{
                                task: "Based on the Magic The Gathering Cards, which one would you recommend and why. Use the context of the user query: {input}"
                            }}
                        ) {{
                        groupedResult
                        error
                        }}
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

mode_descriptions = {
    "BM25": [
        "BM25 is a method used by search engines to rank documents based on their relevance to a given query, factoring in both the frequency of keywords and the length of the document.",
        bm25_gql,
        30,
    ],
    "Vector": [
        "Vector search is a method used by search engines to find and rank results based on their similarity to your search query. Instead of just matching keywords, it understands the context and meaning behind your search, offering more relevant and nuanced results.",
        vector_gql,
        15,
    ],
    "Hybrid": [
        "Hybrid search combines vector and BM25 methods to offer better search results. It leverages the precision of BM25's keyword-based ranking with vector search's ability to understand context and semantic meaning. Providing results that are both directly relevant to the query and contextually related.",
        hybrid_gql,
        15,
    ],
    "Generative": [
        "Generative search is an advanced method that combines information retrieval with AI language models. After finding relevant documents using search techniques like vector and BM25, the found information is used as an input to a language model, which generates further contextually related information.",
        generative_gql,
        9,
    ],
}

# Information
with st.expander("Built with Weaviate for the Streamlit Hackathon 2023"):
    st.subheader("Streamlit Hackathon 2023")
    st.markdown(
        """
        This project is a submission for the [Streamlit Connections Hackathon 2023](https://discuss.streamlit.io/t/connections-hackathon/47574).
        It delivers a Streamlit connector for the open-source vector database, [Weaviate](https://weaviate.io/). 
        Magic Chat uses the Weaviate connector to search through [Magic The Gathering](https://magic.wizards.com/en) cards with various search options, such as BM25, Semantic Search, Hybrid Search and Generative Search. 
        You can find the submission in this [GitHub repo](https://github.com/weaviate/st-weaviate-connection/tree/main)
        """
    )
    st.subheader("Data")
    st.markdown(
        """The database contains around 27k cards from the [Scryfall API](https://scryfall.com/). We used the following attributes to index the cards:
- Name, Type, Keywords
- Mana cost, Mana produced, Color
- Power, Toughness, Rarity
- Set name and Card description """
    )
    st.subheader("How the demo works")
    st.markdown(
        """The demo offers four search options with defined GraphQL queries, which you can use to search for various Magic cards. 
        You can search for card types such as "Vampires", "Humans", "Wizards", or you can search for abilities, mana color, descriptions, and more.
        If you're interested you can read more about the anatomy of a Magic card in this [documentation from the Magic Academy](https://magic.wizards.com/en/news/feature/anatomy-magic-card-2006-10-21).
"""
    )
    st.markdown(
        """The first is the **BM25 search**, 
        it's a method used by search engines to rank documents based on their relevance to a given query, 
        factoring in both the frequency of keywords and the length of the document. In simple terms, we're conducting keyword matching.
        We can simply pass a query to the `query` parameter ([see docs](https://weaviate.io/developers/weaviate/search/bm25))"""
    )
    st.code(
        """
        {
            Get {
                Card(limit: {card_limit}, bm25: { query: "Vampires with flying ability" }) 
                {
                    ...
                }
            }
        }""",
        language="graphql",
    )
    st.markdown(
        """The second option is **Vector search**, a method used to find and rank results based on their similarity to a given search query. 
        Instead of matching keywords, it understands the context and meaning behind the query, offering relevant and more semantic related results. For example, when we search for "Vampires" we might also get cards like a "Bat" or "Undead" because they are semantically related.
        We use the `nearText` function in which we pass our query to the `concepts` parameter ([see docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#neartext))"""
    )
    st.code(
        """
        {
            Get {
                Card(limit: {card_limit}, nearText: { concepts: ["Vampires with flying ability"] }) 
                {
                    ...
                }
            }
        }""",
        language="graphql",
    )
    st.markdown(
        """With **Hybrid search** we combine both methods and use a ranking alogrithm to combine their results. 
        It leverages the precision of BM25's keyword-based ranking with vector search's ability to understand context and semantic meaning. 
        We can pass our query to the `query` parameter and set the `alpha` that determines the weighting for each search ([see docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid))"""
    )
    st.code(
        """
        {
            Get {
                Card(limit: {card_limit}, hybrid: { query: "Vampires with flying ability" alpha:0.5 }) 
                {
                    ...
                }
            }
        }""",
        language="graphql",
    )
    st.markdown(
        """The last option is **Generative search** which is an advanced method that combines information retrieval with AI language models. 
        In our configuration, it retrieves results with a **Vector search** and passes them to a `gpt-3.5-turbo model` to determine the best Magic card based on the user query. For this, we rely on its knowledge about Magic The Gathering, but this model could be easily exchanged. 
        We use the `generate` module and `groupedResult` task which uses the data of the result as context for the given prompt and query. ([see docs](https://weaviate.io/developers/weaviate/modules/reader-generator-modules/generative-openai))"""
    )
    st.code(
        """
        {
            Get {
                Card(limit: {card_limit}, nearText: { concepts: ["Vampires with flying ability"] }) 
                {
                    _additional {
                        generate(
                            groupedResult: {
                                task: "Based on the Magic The Gathering Cards, which one would you recommend and why. Use the context of the user query: {input}"
                            }
                        ) {
                        groupedResult
                        error
                        }
                    }
                }
            }
        }""",
        language="graphql",
    )
    st.subheader("Future ideas")
    st.markdown(
        """Magic The Gathering is a very complex and exciting game, and there were many ideas we got when building this demo. 
        We thought about an actual deck builder interface, where you could search for similar cards or predict the next card based on your already established deck. 
        Or even a meta-finder that simulates battles between two sets of cards, trying out different combinations and more. With Magic, the possibilities for an exciting demo are endless, and we hope to enhance the demo further!
"""
    )

col1, col2, col3 = st.columns([0.2, 0.5, 0.2])

col2.image("./img/anim.gif")

# User Configuration Sidebar
with st.sidebar:
    mode = st.radio(
        "Search Mode", options=["BM25", "Vector", "Hybrid", "Generative"], index=3
    )
    limit = st.slider(
        label="Number of cards",
        min_value=1,
        max_value=mode_descriptions[mode][2],
        value=6,
    )
    st.info(mode_descriptions[mode][0])

st.divider()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False

# Display chat messages from history on app rerun
display_chat_messages()

# Greet user
if not st.session_state.greetings:
    with st.chat_message("assistant"):
        intro = "Hey! I am Magic Chat, your assistant for finding the best Magic The Gathering cards to build your dream deck. Let's get started!"
        st.markdown(intro)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": intro})
        st.session_state.greetings = True

# Example prompts
example_prompts = [
    "You gain life and enemy loses life",
    "Vampires cards with flying ability",
    "Blue and green colored sorcery cards",
    "White card with protection from black",
    "The famous 'Black Lotus' card",
    "Wizard card with Vigiliance ability",
]

example_prompts_help = [
    "Look for a specific card effect",
    "Search for card type: 'Vampires', card color: 'black', and ability: 'flying'",
    "Color cards and card type",
    "Specifc card effect to another mana color",
    "Search for card names",
    "Search for card types with specific abilities",
]

button_cols = st.columns(3)
button_cols_2 = st.columns(3)

button_pressed = ""

if button_cols[0].button(example_prompts[0], help=example_prompts_help[0]):
    button_pressed = example_prompts[0]
elif button_cols[1].button(example_prompts[1], help=example_prompts_help[1]):
    button_pressed = example_prompts[1]
elif button_cols[2].button(example_prompts[2], help=example_prompts_help[2]):
    button_pressed = example_prompts[2]

elif button_cols_2[0].button(example_prompts[3], help=example_prompts_help[3]):
    button_pressed = example_prompts[3]
elif button_cols_2[1].button(example_prompts[4], help=example_prompts_help[4]):
    button_pressed = example_prompts[4]
elif button_cols_2[2].button(example_prompts[5], help=example_prompts_help[5]):
    button_pressed = example_prompts[5]


if prompt := (st.chat_input("What cards are you looking for?") or button_pressed):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    images = []
    if prompt != "":
        query = prompt.strip().lower()
        gql = mode_descriptions[mode][1].format(input=query, limit_card=limit)

        df = conn.query(gql, ttl=None)

        response = ""
        with st.chat_message("assistant"):
            for index, row in df.iterrows():
                if index == 0:
                    if "_additional.generate.groupedResult" in row:
                        first_response = row["_additional.generate.groupedResult"]
                    else:
                        first_response = f"Here are the results from the {mode} search:"

                    message_placeholder = st.empty()
                    full_response = ""
                    for chunk in first_response.split():
                        full_response += chunk + " "
                        time.sleep(0.02)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    response += full_response + " "

                # Create a new row of columns for every NUM_IMAGES_PER_ROW images
                if index % NUM_IMAGES_PER_ROW == 0:
                    cols = st.columns(NUM_IMAGES_PER_ROW)

                if row["img"]:
                    # Display image in the column
                    cols[index % NUM_IMAGES_PER_ROW].image(row["img"], width=200)
                    images.append(row["img"])
                else:
                    cols[index % NUM_IMAGES_PER_ROW].write(
                        f"No Image Available for: {row['type']}"
                    )

            st.session_state.messages.append(
                {"role": "assistant", "content": response, "images": images}
            )
            st.experimental_rerun()
