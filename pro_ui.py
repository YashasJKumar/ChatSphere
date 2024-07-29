import ollama
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Private AI Assistant",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


def extract_model_names(models_info: list) -> tuple:
    return tuple(model["name"] for model in models_info['models'])


def main():
    st.header("Private AI Assistant", divider="green", anchor=False)
    with st.sidebar:
        st.image("./ollama.png", use_column_width=True)
        st.title("Fully Secure Chat")
        st.markdown(":orange[Powered by Ollama.]")
        st.write("")
        st.write("Ask any question to the LLM'S running natively on your machine.")
        st.write("No Data leaves your Computer.")

    # Initialization
    client = None
    selected_model = None

    try:
        client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"  # Required but never used.Can give anything.
        )

        models_info = ollama.list()
        available_models = extract_model_names(models_info)

        if available_models:
            st.sidebar.write("")
            st.sidebar.markdown(":blue[Choose your LLM here 👇]")
            selected_model = st.sidebar.selectbox(
                label="Select a model available locally on your system: ", index=0, options=available_models
            )
        else:
            st.warning("No models available on your system")
    except Exception as e:
        st.error("Error : Could not connect to Ollama. Please turn ON Ollama Server & Refresh the Page." + str(e),
                 icon="‼️")

    message_container = st.container(height=500, border=False)

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if st.session_state['messages'] is not None:
        st.sidebar.write("")
        if st.sidebar.button("Clear Chat"):
            st.session_state["messages"].clear()

    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "😎"
        with message_container.chat_message(message["role"], avatar=avatar):
            st.markdown(message['content'])

    if prompt := st.chat_input("Enter your prompt: "):
        try:
            st.session_state["messages"].append(
                {'role': "user", 'content': prompt}
            )

            message_container.chat_message("user", avatar="😎").markdown(prompt)

            with message_container.chat_message("assistant", avatar="🤖"):
                with st.spinner("Working on it.."):
                    stream = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state["messages"]
                        ],
                        stream=True
                    )
                response = st.write_stream(stream)
            st.session_state.messages.append(
                {"role": "assistant", "content": response}
            )

        except Exception as e:
            st.error(e, icon="‼️")


if __name__ == "__main__":
    main()
