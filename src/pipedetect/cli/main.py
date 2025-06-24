"""Main CLI entry point."""

from pathlib import Path
from typing import Optional
import sys

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..core.models import DetectionConfig
from ..core.exceptions import PipeDetectError
from ..utils.logging_config import setup_logging, get_log_level_from_verbosity
from .processor import PoseProcessor

app = typer.Typer(
    name="pipedetect",
    help="Professional pose estimation using MediaPipe",
    add_completion=False
)

console = Console()


@app.command()
def main(
    input_path: Path = typer.Argument(
        ...,
        help="Input video file, image file, or directory of images",
        exists=True
    ),
    output_dir: Path = typer.Option(
        "outputs",
        "--output-dir", "-o",
        help="Output directory for results"
    ),
    json_output: Optional[str] = typer.Option(
        None,
        "--json",
        help="JSON output filename (default: pose_<timestamp>.json)"
    ),
    csv_output: Optional[str] = typer.Option(
        None,
        "--csv", 
        help="CSV output filename (default: pose_<timestamp>.csv)"
    ),
    min_detection_confidence: float = typer.Option(
        0.5,
        "--detection-confidence",
        min=0.0,
        max=1.0,
        help="Minimum detection confidence"
    ),
    min_tracking_confidence: float = typer.Option(
        0.5,
        "--tracking-confidence", 
        min=0.0,
        max=1.0,
        help="Minimum tracking confidence"
    ),
    model_complexity: int = typer.Option(
        1,
        "--model-complexity",
        min=0,
        max=2,
        help="Model complexity (0=light, 1=full, 2=heavy)"
    ),
    enable_segmentation: bool = typer.Option(
        False,
        "--segmentation",
        help="Enable pose segmentation"
    ),
    no_smooth_landmarks: bool = typer.Option(
        False,
        "--no-smooth",
        help="Disable landmark smoothing"
    ),
    no_frames: bool = typer.Option(
        False,
        "--no-frames",
        help="Don't save individual frames"
    ),
    no_overlays: bool = typer.Option(
        False,
        "--no-overlays", 
        help="Don't save overlay frames"
    ),
    no_progress: bool = typer.Option(
        False,
        "--no-progress",
        help="Hide progress bar"
    ),
    log_file: Optional[Path] = typer.Option(
        None,
        "--log-file",
        help="Log file path"
    ),
    verbose: int = typer.Option(
        0,
        "--verbose", "-v",
        count=True,
        help="Increase verbosity (-v, -vv)"
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet", "-q",
        help="Suppress console output"
    )
) -> None:
    """Detect poses in videos or images using MediaPipe.
    
    This tool processes video files, single images, or directories of images
    to detect human poses using Google's MediaPipe framework. Results are
    saved as JSON and CSV files, with optional frame extraction and pose overlays.
    
    Examples:
        pipedetect video.mp4
        pipedetect image.jpg --output-dir results/
        pipedetect images/ --json poses.json --csv poses.csv
        pipedetect video.mp4 --model-complexity 2 --detection-confidence 0.7
    """
    try:
        # Setup logging
        log_level = get_log_level_from_verbosity(verbose)
        setup_logging(
            log_level=log_level,
            log_file=log_file,
            enable_console=not quiet
        )
        
        # Display banner
        if not quiet:
            _display_banner()
        
        # Create detection configuration
        config = DetectionConfig(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
            model_complexity=model_complexity,
            enable_segmentation=enable_segmentation,
            smooth_landmarks=not no_smooth_landmarks
        )
        
        # Display configuration
        if not quiet:
            _display_config(config, input_path, output_dir)
        
        # Process input
        with PoseProcessor(
            config=config,
            output_dir=output_dir,
            save_frames=not no_frames,
            save_overlays=not no_overlays,
            show_progress=not no_progress and not quiet
        ) as processor:
            stats = processor.process_input(
                input_path=input_path,
                json_output=json_output,
                csv_output=csv_output
            )
        
        # Display results summary
        if not quiet:
            _display_results(stats)
        
        # Exit with appropriate code
        if stats.success_rate < 0.5:
            console.print("[yellow]Warning: Low success rate (<50%)[/yellow]")
            sys.exit(1)
        
    except PipeDetectError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Processing interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        if verbose >= 2:
            console.print_exception()
        sys.exit(1)


def _display_banner() -> None:
    """Display application banner."""
    banner_text = Text()
    banner_text.append("PipeDetect", style="bold blue")
    banner_text.append(" - Professional Pose Estimation with MediaPipe", style="dim")
    
    panel = Panel(
        banner_text,
        expand=False,
        border_style="blue"
    )
    
    console.print()
    console.print(panel)
    console.print()


def _display_config(config: DetectionConfig, input_path: Path, output_dir: Path) -> None:
    """Display processing configuration.
    
    Args:
        config: Detection configuration
        input_path: Input path
        output_dir: Output directory
    """
    config_text = Text()
    config_text.append("Configuration:\n", style="bold")
    config_text.append(f"  Input: {input_path}\n")
    config_text.append(f"  Output: {output_dir}\n")
    config_text.append(f"  Detection confidence: {config.min_detection_confidence}\n")
    config_text.append(f"  Tracking confidence: {config.min_tracking_confidence}\n")
    config_text.append(f"  Model complexity: {config.model_complexity}\n")
    config_text.append(f"  Segmentation: {config.enable_segmentation}\n")
    config_text.append(f"  Smooth landmarks: {config.smooth_landmarks}")
    
    panel = Panel(
        config_text,
        title="Settings",
        border_style="green"
    )
    
    console.print(panel)
    console.print()


def _display_results(stats) -> None:
    """Display processing results summary.
    
    Args:
        stats: Processing statistics
    """
    results_text = Text()
    results_text.append("Processing Results:\n", style="bold green")
    results_text.append(f"  Total frames: {stats.total_frames}\n")
    results_text.append(f"  Processed frames: {stats.processed_frames}\n")
    results_text.append(f"  Failed frames: {stats.failed_frames}\n")
    results_text.append(f"  Success rate: {stats.success_rate:.1%}\n")
    results_text.append(f"  Processing time: {stats.processing_time:.2f}s\n")
    results_text.append(f"  Average FPS: {stats.fps:.1f}")
    
    panel = Panel(
        results_text,
        title="Summary",
        border_style="green" if stats.success_rate > 0.5 else "yellow"
    )
    
    console.print()
    console.print(panel)


if __name__ == "__main__":
    app() 