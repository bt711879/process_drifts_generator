import sys
import click

# Adding 'C:\\GitRepositories\\process_drifts_generator\\src' to the system path
sys.path.insert(0, 'C:\\GitRepositories\\process_drifts_generator')
  
# main.py
import pm4py
from pm4py.objects.bpmn.obj import BPMN
from pm4py.objects.process_tree.obj import ProcessTree, Operator
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.algo.simulation.tree_generator import algorithm as tree_gen
from pm4py.objects.process_tree.importer import importer as ptml_importer
from pm4py.objects.conversion.bpmn import converter as bpmn_converter
from pm4py.objects.conversion.wf_net import converter as wf_net_converter
from pm4py.objects.petri_net.importer import importer as pnml_importer
from random import randint
from src.transformations.add_fragment import AddFragment
from src.transformations.remove_fragment import RemoveFragment
from src.transformations.add_fragment import AddFragment
from src.transformations.move_fragment import MoveFragment
from src.transformations.replace_fragment import ReplaceFragment
from src.transformations.swap_two_fragments import SwapFragments
from src.transformations.embed_process_fragment import EmbedFragment, EmbedType
from src.transformations.parallelize_process_fragments import ParellelizeFragment
from src.fragment_factory import FragmentFactory
from src.activity_key import ActivityKey
import src.util as util
from src.move import Move

import networkx as nx

# Create a data structure to store values
class Context:
    def __init__(self):
        self.process = None
        self.transformation = None
        self.fragments = None

# Initialize the context
context = Context()

@click.group()
@click.pass_context
def mycommands(ctx):
    # Pass the context to subcommands
    ctx.obj = context

@click.command()
@click.option('--path', prompt="Enter the file path", help='The file path containing the process as .bpmn file')
@click.pass_context
def load_bpmn(ctx, path):
    """Load a BPMN process"""
    ctx.obj.process = pm4py.read_bpmn(path)

@click.command()
@click.pass_context
def select_transformation(ctx):
    """Select a transformation"""
    transformations = ['Add Fragment', 'Delete Fragment', 'Swipe Fragments']
    choice = click.prompt('Select a transformation:', type=click.Choice(transformations))
    ctx.obj.transformation = choice

@click.command()
@click.pass_context
def select_fragments(ctx):
    """Select fragments to apply the transformation"""
    fragments = ['Fragment 1', 'Fragment 2', 'Fragment 3']
    selected_fragments = click.prompt('Select fragments (comma-separated):')
    ctx.obj.fragments = [fragment.strip() for fragment in selected_fragments.split(',')]

@click.command()
@click.pass_context
def view_parameters(ctx):
    """View selected parameters for transformation"""
    click.echo(f"Process: {ctx.obj.process}")
    click.echo(f"Transformation: {ctx.obj.transformation}")
    click.echo(f"Fragments: {ctx.obj.fragments}")

mycommands.add_command(load_bpmn)
mycommands.add_command(select_transformation)
mycommands.add_command(select_fragments)
mycommands.add_command(view_parameters)

# Main function to handle command execution
def main():
    mycommands(prog_name='python main.py')

if __name__ == "__main__":
    main()
