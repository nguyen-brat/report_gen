import matplotlib.pyplot as plt
from PIL import Image
import subprocess

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import os
from glob import glob
import shutil
import numpy as np
import cv2
from tqdm import tqdm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import DBSCAN

class OCRHandler:
    ##################################################
    def process_ocr_results(
            self,
            ocr_results,
            n_neighbors=1,
            eps=2.8,
            min_samples=2
    ):
        '''
        Cluster ocr result into group of text. Include 2 stage:
        stage 1: divide the ocr result into paragraph by using dbscan for unsupervise group and
        k-nearest neighbor for handle outlier
        stage 2: for each group of paragraph gather the ocr result into line by line by sorting
        the x and y coordinate then mesure if there any different in the present and privous height
        of text bounding box to devide the new line.
        '''
        y_length = []
        for output in ocr_results:
            process_data = self.get_center_coordinate(output)
            y_length.append(process_data[1])
        mean_length = np.array(y_length).mean()
        _, labels = self.cluster(ocr_results, n_neighbors=n_neighbors, eps=eps*mean_length, min_samples=min_samples)
        num_labels_ = int(max(labels)) + 1

        results = ''
        for index in range(num_labels_):
            categories_i_sample = [ocr_results[i] for i in np.argwhere(labels==index).flatten().tolist()]
            processed_paragraphs = self._process_ocr_results(categories_i_sample)
            results += processed_paragraphs + '\n'
        return results


    def _process_ocr_results(self, ocr_results):
        '''
        Logic to sort text in the same line in the same order is to sort every value by y first
        Logic to choose the text on the same line is if next ocr result has diff height  exceed last height/2
        it mean it categories to the new line.
        '''

        sorted_results = sorted(ocr_results, key=lambda x: (x[0][1], x[0][0]))
        lines = []
        current_line = []
        prev_y = None
        for bbox, text in sorted_results:
            x, y = bbox[0], bbox[1]  # Use top-left corner coordinates
            h = bbox[5] - bbox[1]  # Calculate height
            if prev_y is None or abs(y - prev_y) > h / 2:
                if current_line:
                    lines.append(current_line)
                current_line = [(text, x)]
            else:
                current_line.append((text, x))
            prev_y = y

        if current_line:
            lines.append(current_line)

        # Concatenate text within lines
        processed_lines = []
        for line in lines:
            sorted_line = sorted(line, key=lambda x: x[1])
            processed_lines.append(" ".join(text for text, _ in sorted_line))

        # Join lines to form paragraphs (simple approach)
        paragraphs = []
        current_paragraph = []
        for line in processed_lines:
            if line.strip():
                current_paragraph.append(line)
            elif current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []

        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))
        # Combine paragraphs to form the final document
        return "\n\n".join(paragraphs)
    

    def cluster(
            self,
            ocr_results,
            n_neighbors=5,
            eps=0.3,
            min_samples=10
    ):
        '''
        Given the ocr result
        '''
        coordinates = []
        y_lengths = []
        for result in ocr_results:
            proces_data = self.get_center_coordinate(result)
            y_lengths.append(proces_data[1])
            coordinates.append(proces_data[0])
        X = np.array(coordinates)
        # Perform DBSCAN clustering
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X)
        labels = db.labels_
        if np.any(labels == -1):
            outliear_mask = (labels == -1)
            non_outliear_mask = (labels != -1)
            outliear_sample = X[outliear_mask]
            sample_x = X[non_outliear_mask]
            sample_y = labels[non_outliear_mask]
            outlinear_label = self.assign_outlier(dict(x=sample_x, y=sample_y), outliear_sample, n_neighbors=n_neighbors)
            labels[outliear_mask] = outlinear_label

        return (X, labels)
    

    def to_float(self, string_number):
        string_number = string_number.split(',')
        return [int(number) for number in string_number]


    def get_center_coordinate(self, sample):
        coordinate = sample[0]
        x_center = (coordinate[0] + coordinate[2] + coordinate[4] + coordinate[6])/4
        y_center = (coordinate[1] + coordinate[3] + coordinate[5] + coordinate[7])/4
        y_length = (coordinate[7] - coordinate[1] + coordinate[5] - coordinate[3])/2
        return [x_center, y_center], y_length


    def assign_outlier(self, dataset, outliear, n_neighbors=5):
        neigh = KNeighborsClassifier(n_neighbors=n_neighbors)
        neigh.fit(dataset["x"], dataset["y"])
        outliear_label = neigh.predict(outliear)
        return outliear_label


    def visualize(self, X, labels, eps, min_samples):
        # Count the number of clusters
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
        # Plot the results
        plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis')
        # Label noise points
        noise_indices = [i for i, label in enumerate(labels) if label == -1]
        plt.scatter(X[noise_indices, 0], X[noise_indices, 1], marker='o', c='black', label='Noise')
        # Add labels and title
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.title(f'DBSCAN Clustering (eps={eps}, min_samples={min_samples})')
        plt.legend()
        # Show the plot
        plt.show()
        print(f"Estimated number of clusters: {n_clusters_}")



class PdfOCR(OCRHandler):
    def __init__(
            self,
            model_path = 'src/crawl/weights/transformerocr.pth',
            model_type = 'vgg_transformer',
            deivce = 'cuda:0',
            script_path='script/script.sh',
    ):
        self.model_path = model_path
        self.device = deivce
        self.script_path = script_path
        self.ocr_engine_loading(model_path=model_path, device=deivce, model_type=model_type)


    def __call__(
            self,
            image_path,
            n_neighbors=1, # n-neighbor for outlier classify using k-nearest neighbor
            eps=2.8, # eps in dbscan (eps = mean_bbox_text_length * eps)
            min_samples=2 # min sample parameter used in dbscan
    ):
        outputs = self.extract_text(image_path)
        final_output = self.process_ocr_results(outputs, n_neighbors=n_neighbors, eps=eps, min_samples=min_samples)

        #clean temp file
        shutil.rmtree("output_tmp")
        shutil.rmtree("input_tmp")

        return final_output
    

    def extract_text(self, image_path):

        img_path = image_path
        pil_img = Image.open(img_path)
        img = np.array(pil_img)
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        elif len(img.shape) == 3 and img.shape[2] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        os.makedirs("input_tmp", exist_ok=True)
        pil_img.save("input_tmp/image.png")
        
        bboxs = self.extract_text_bounding_box()
        texts = []
        
        for bbox in tqdm(bboxs):
            roi = self.extract_text_from_bboxes(image_path, bbox)
            # Convert the ROI back to PIL Image for the detector
            roi_pil = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
            texts.append(self.detector.predict(roi_pil))

        return list(zip(bboxs, texts))
    

    def extract_text_bounding_box(self):
        os.makedirs("output_tmp", exist_ok=True)
        bash_command = f'bash {self.script_path}'
                                                                
        _ = subprocess.run(bash_command, shell=True, check=True)
        folder_path = glob("output_tmp/*.txt")[0]
        with open(folder_path, "r") as f:
            bboxs = f.read().strip().split()
        bboxs = [self.to_float(bbox) for bbox in bboxs]

        return bboxs
    

    def extract_text_from_bboxes(self, image_path, bbox):
        # Load the image
        image = cv2.imread(image_path)
        pts = [(bbox[0], bbox[1]), (bbox[2], bbox[3]), (bbox[4], bbox[5]), (bbox[6], bbox[7])]
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, [np.array(pts)], (255, 255, 255))
        roi = cv2.bitwise_and(image, mask)
        x_min, y_min = min(pt[0] for pt in pts), min(pt[1] for pt in pts)
        x_max, y_max = max(pt[0] for pt in pts), max(pt[1] for pt in pts)
        roi_cropped = roi[y_min:y_max, x_min:x_max]
        
        return roi_cropped
    
    def ocr_engine_loading(self, model_path, device, model_type='vgg_transformer'):
        config = Cfg.load_config_from_name(model_type)
        config['weights'] = model_path
        config['cnn']['pretrained'] = False
        config['device'] = device
        self.detector = Predictor(config)

if __name__ == "__main__":
    reader = PdfOCR()
    output = reader('37302-1.png')
    print(output)