import gcs_module as gcs 
import datetime

if __name__ == '__main__':
    # upload aicollective model (aicollective.pkl) to bucket and rename it as model1.pkl
    gcs.upload_blob('analytics.arkana.ai', './models/aicollective.pkl', 'savedmodel/{}.pkl'.format(datetime.datetime.now()))

    # download model1.pkl from bucket and download as testing_download.pkl in models folder
    gcs.download_blob('analytics.arkana.ai', 'model1.pkl', 'models/{}_dwnloaded_model.pkl'.format(datetime.datetime.now()))