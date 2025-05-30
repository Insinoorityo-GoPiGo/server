from control_panel import Control_Panel
from get_coordinates_and_edges import get_coordinates_and_edges
from PathFinding import PathFinding
from ImageAnalysisHandler import ImageAnalysisHander
import threading

from queue import Queue

def main():
    #Openai ja kuvankäsittely -threadin käynnistys
    obstacle_description_queue = Queue()
    image_analysis_handler = ImageAnalysisHander(obstacle_description_queue=obstacle_description_queue)
    threading.Thread(target=image_analysis_handler.start, daemon=True).start()

    PathFinding.COORDINATES, PathFinding.EDGES = get_coordinates_and_edges()

    Control_Panel(obstacle_description_queue=obstacle_description_queue).open_control_panel()

if __name__ == "__main__":
    main()