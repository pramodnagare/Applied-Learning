from Application.app import TextImageSorting
import time

if __name__ == "__main__":
    start = time.time()
    conf_file = r"configuration/conf.json"
    a = TextImageSorting(conf_file)
    a.extract_text_images() # for parallel file extraction
    # a.extract_text_images_seq() # for sequential file extraction
    a.setupOutputDir()
    a.sortImages()
    end = time.time()
    print("Total time for execution: {} secs!".format(end-start))