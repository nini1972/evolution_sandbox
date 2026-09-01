import requests

def download_addbiomechanics_dataset():
    url = 'http://archive.simtk.org/addbiomechanics/addbiomechanics.zip'
    response = requests.get(url)
    with open('AddBiomechanicsDataset.zip', 'wb') as f:
        f.write(response.content)

if __name__ == '__main__':
    download_addbiomechanics_dataset()