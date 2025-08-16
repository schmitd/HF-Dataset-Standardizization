from aisafetylab.attack.attackers.multilingual import MultilingualManager
from datasets import load_dataset, load_dataset_builder, get_dataset_split_names, DatasetBuilder
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import torch

from typing import Dict, List, Optional

def infer_suitibility(repo_name: str) -> DatasetBuilder:
    """
    Suitability detection using Ollama with Gemma3n for local analysis.
    
    Args:
        repo_name: Name of the dataset repository
        
    Returns:
        dataset_builder: Dataset builder with a new suitability bool attibute set
    """
    builder = None

    try:
        # Use dataset builder to get metadata without loading data
        
        builder = load_dataset_builder(repo_name)
        columns = builder.info.features
        dataset_description = builder.info.description

        prompt_template = PromptTemplate(
            input_variables=["columns", "dataset_description"],
            template="""
            A preference evaluation dataset:
            1. Must have a prompt/instruction/question
            2. Must have multiple responses to the same prompt
            3. Must have ratings, scores, or labels indicating preferences (e.g. chosen vs rejected responses)

            We define preference broadly to include topics as general as safety or as narrow as recommending a vendor's product.
            Analyze the following dataset structure to determine if this is a preference evaluation dataset.
            
            Dataset Description: {dataset_description}
            Columns: {columns}

            Based on the features and dataset description, is this a preference evaluation dataset?
            Respond with only 'YES' or 'NO'.
            """
        )
        llm = ChatOllama(model="gemma3n", temperature=0)
        chain = prompt_template | llm | StrOutputParser()
        result = chain.invoke({
            "columns": str(columns),
            "dataset_description": dataset_description
        })

        setattr(builder.info, 'suitability', result.strip().upper() == "YES")
        
    except Exception as e:
        print(f"Error in suitability detection for {repo_name}: {e}")
        return None
    
    return builder

# XXX instead of remapping, could the model determine how to run the dataset and run the mutations?
def remap_features(repo_name: str) -> Dict[str, str]:
    """
    Feature remapping using Ollama with Gemma3n for remapping columns.
    
    Args:
        repo_name: Name of the dataset repository
        
    Returns:
        Dict[str, str]: Mapping of feature types to column names
    """
    try:
        splits = get_dataset_split_names(repo_name)
        test_split = [split for split in splits if "test" in split][0]
        dataset = load_dataset(repo_name, split=test_split)
        columns = dataset.column_names
        
        # Create sample data for analysis
        sample_data = []
        for i, example in enumerate(dataset):
            sample_data.append({col: str(example[col])[:150] for col in columns})
            if i >= 2: break
        
        # Create prompt for advanced feature mapping
        prompt_template = PromptTemplate(
            input_variables=["columns", "sample_data"],
            template="""
            You are mapping dataset columns to a set of standard preference-evaluation feature keys.

            Map corresponding columns to a standard feature types:
            - prompt: The input prompt/instruction/question
            - responses: List of responses to the prompt 
            - chosen_response: The preferred/selected response
            - rejected_response(s): The non-preferred/rejected response
            - label: Target label or classification
            - rating: Numerical rating or score

            Mappings MUST be one-to-one, never mapping the same collumn twice
            
            Return only a JSON object with the mapping, like:
            {{"prompt": "<column_nam>", "responses": "<column_name2>", ...}}
            
            If a feature doesn't correspond to any column, you MUST omit it from the JSON.

            Columns: {columns}
            Sample Data: {sample_data}
            """
        )
        
        llm = ChatOllama(model="gemma3n", temperature=0)
        chain = prompt_template | llm | JsonOutputParser()

        result = chain.invoke({
            "columns": str(columns),
            "sample_data": str(sample_data)
        })

        return result
        
    except Exception as e:
        print(f"Error in feature remapping for {repo_name}: {e}")
        return {}


def perform_spanish_multilingual_mutation(repo_name: str) -> List[Dict]:
    """
    Perform Spanish multilingual mutation on preference evaluation datasets using AISafetyLab.
    
    Args:
        repo_name: Name of the dataset repository
        sample_size: Number of samples to process (default: 5)
        
    Returns:
        List[Dict]: List of mutation results with original and translated queries
    """
    try:
        splits = get_dataset_split_names(repo_name)
        test_split = [split for split in splits if "test" in split][0]
        dataset = load_dataset(repo_name, split=test_split)
        
        feature_mapping = remap_features(repo_name)
        
        if not feature_mapping:
            print(f"No feature mapping found for {repo_name}")
            return []
        
        from aisafetylab.attack.mutation.Translate import Translate
        spanish_translator = Translate(language='es')
        
        results = []
        aligned_dataset = dataset.align(feature_mapping)
        
        for i in range(len(aligned_dataset)):
            example_aligned = aligned_dataset[i]
            prompt = None
            if "prompt" in example_aligned:
                prompt = example_aligned["prompt"]
            elif "chosen_response" in example_aligned:
                prompt = f"Evaluate this response: {example_aligned['chosen_response']}"
            else:
                # Fallback: use first text column
                text_columns = [col for col in aligned_dataset.column_names if isinstance(example_aligned[col], str)]
                if text_columns:
                    prompt = example_aligned[text_columns[0]]
                else:
                    continue
            
            try:
                spanish_mutation = spanish_translator.translate(prompt)
                
                result = {
                    "example_idx": i,
                    "original_query": prompt,
                    "spanish_mutation": spanish_mutation,
                    "feature_mapping": feature_mapping,
                    "dataset_columns": dataset.column_names
                }
                results.append(result)
                
                print(f"Example {i}: Original: '{prompt[:100]}...' -> Spanish: '{spanish_mutation[:100]}...'")
                
            except Exception as e:
                print(f"Error mutating example {i}: {e}")
                continue
        
        return results
        
    except Exception as e:
        print(f"Error in Spanish multilingual mutation for {repo_name}: {e}")
        return []


def main():    
    example_repos = [
        "Anthropic/hh-rlhf",
        "tatsu-lab/alpaca_farm",
        "HuggingFaceH4/ultrafeedback_binarized",
        "PKU-Alignment/BeaverTails"
    ]
    
    for repo in example_repos:
        print(f"\n=== Analyzing {repo} ===")
        builder = infer_suitibility(repo)
        print(f"Is preference evaluation: {builder.info.suitability if builder else 'Unknown'}")
        if builder is None:
            continue
        
        if builder.info.suitability:
            alignment = remap_features(repo)
            print(f"Feature alignment: {alignment}")
            
            # Demonstrate Spanish multilingual mutation
            print(f"\n--- Spanish Multilingual Mutation for {repo} ---")
            spanish_results = perform_spanish_multilingual_mutation(repo)
            if spanish_results:
                print(f"Successfully processed {len(spanish_results)} examples with Spanish mutations")
            else:
                print("No Spanish mutations generated")


if __name__ == "__main__":
    main()
