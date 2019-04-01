import gcs_module as gcs 

if __name__ == '__main__':
    # upload aicollective model (aicollective.pkl) to bucket and rename it as model1.pkl
    gcs.upload_blob('analytics.arkana.ai', './models/aicollective.pkl', 'model1.pkl')

    # download model1.pkl from bucket and download as testing_download.pkl in models folder
    gcs.download_blob('analytics.arkana.ai', 'model1.pkl', 'models/testing_download.pkl')