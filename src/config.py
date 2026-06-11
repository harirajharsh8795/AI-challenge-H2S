import os
from datetime import date, datetime
from typing import Union
import yaml
from pydantic import BaseModel, Field, field_validator
from src.logger import PipelineLogger

logger = PipelineLogger.get_logger()


class PipelineConfig(BaseModel):
    """Pipeline orchestration configurations."""

    current_date: date = Field(..., description="The reference date for the data state calculation.")
    random_seed: int = Field(42, description="Random seed for reproducibility.")

    @field_validator("current_date", mode="before")
    @classmethod
    def parse_current_date(cls, value: Union[str, date]) -> date:
        """Parses current_date string into a datetime.date object."""
        if isinstance(value, str):
            try:
                return datetime.strptime(value.strip(), "%Y-%m-%d").date()
            except ValueError as e:
                raise ValueError(f"current_date must be in ISO format YYYY-MM-DD: {str(e)}")
        elif isinstance(value, date):
            return value
        raise TypeError("current_date must be a YYYY-MM-DD string or datetime.date object.")


class ModelsConfig(BaseModel):
    """Model execution specifications."""

    embedding_model: str = Field(..., description="Sentence-Transformers model name to load.")
    cross_encoder_model: str = Field(..., description="Cross-Encoder model name to load.")
    device: str = Field("cpu", description="Compute device ('cpu' or 'cuda'). Enforced to 'cpu' by constraints.")


class RetrievalConfig(BaseModel):
    """Stage 1 and 2 retrieval parameters and candidate filters."""

    stage1_top_k: int = Field(2000, ge=100, le=10000, description="Stage 1 BM25 candidates to extract.")
    stage2_top_k: int = Field(500, ge=50, le=5000, description="Stage 2 dense similarity candidates to rerank.")
    final_top_k: int = Field(100, ge=1, le=1000, description="Final number of top candidates to export.")
    min_experience_years: float = Field(3.0, ge=0.0, description="Minimum years of experience filter.")
    max_experience_years: float = Field(12.0, ge=0.0, description="Maximum years of experience filter.")


class WeightsConfig(BaseModel):
    """Scoring component weights totaling 100."""

    semantic_match: float = Field(..., ge=0.0, le=100.0)
    experience_fit: float = Field(..., ge=0.0, le=100.0)
    product_company: float = Field(..., ge=0.0, le=100.0)
    behavioral_signals: float = Field(..., ge=0.0, le=100.0)
    preferred_skills: float = Field(..., ge=0.0, le=100.0)
    location: float = Field(..., ge=0.0, le=100.0)

    @field_validator("semantic_match", "experience_fit", "product_company", "behavioral_signals", "preferred_skills", "location")
    @classmethod
    def check_non_negative(cls, value: float) -> float:
        """Validates that weights are non-negative."""
        if value < 0.0:
            raise ValueError("Component scoring weight must be non-negative.")
        return value


class AppConfig(BaseModel):
    """Root configuration model representing configs/ranking_config.yaml."""

    pipeline: PipelineConfig
    models: ModelsConfig
    retrieval: RetrievalConfig
    weights: WeightsConfig


def load_config(filepath: str = "configs/ranking_config.yaml") -> AppConfig:
    """Loads and validates configuration from a local YAML file.

    Args:
        filepath (str): Path to the YAML configuration file.

    Returns:
        AppConfig: The parsed and validated configurations.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If YAML syntax is invalid or Pydantic validation fails.
    """
    if not os.path.exists(filepath):
        logger.error("Configuration file '%s' was not found on disk.", filepath)
        raise FileNotFoundError(f"Configuration file not found: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
            
        if raw_data is None:
            raise ValueError("YAML config file is empty.")

        config_obj = AppConfig(**raw_data)
        logger.info("Configuration successfully loaded and validated from '%s'.", filepath)
        return config_obj

    except yaml.YAMLError as e:
        logger.error("Failed to parse YAML configuration: %s", str(e))
        raise ValueError(f"Invalid YAML syntax: {str(e)}")
    except Exception as e:
        logger.error("Validation error when parsing configuration: %s", str(e))
        raise ValueError(f"Configuration validation failed: {str(e)}")
