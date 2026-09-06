import requests

def download_addbiomechanics_dataset():
    url = 'http://archive.simtk.org/addbiomechanics/addbiomechanics.zip'
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open('AddBiomechanicsDataset.zip', 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    else:
        print('Failed to download the dataset')

if __name__ == '__main__':
    download_addbiomechanics_dataset()