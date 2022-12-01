#Advanced Data Science Library (ADSLIB)

Contains methods used for the evaluation of house prices using features from OpenStreetMap.

<b>ATTRIBUTION:</b> © OpenStreetMap contributors, Credit to OpenStreetMap https://www.openstreetmap.org/copyright
Data avialable under the Open Database License.

## Table of Contents
<ol>
<li>Installation</li>
<li>Repository</li>
<li>Version Control</li>
</ol>

## Installation

The library is pip-installable via the command:
`pip install --upgrade git+https://github.com/1414vo/adslib`

## Repository

Every described file in the reposityory is held in the `adslib` folder.

#### \_\_init\_\_.py

Serves as the main file of the package and imports all other contained modules.

#### <span>credentialstore.py</span>

Serves to allow encryption and decryption in storing credentials, as well as to control how they are loaded and stored. It uses a constant key, so decryption is theoretically possible, in the case of a hacker looking up this library, but is the simplest way to go about the credentials not being directly accessible without requiring some form of authentication.

#### <span>access_store.py</span>

Contains methods to load data into tables and to create a connection to a database using provided connections.

#### <span>access_load.py</span>

This module is used for querying the tables in the `property_prices` database. They are used to query based on the indexed columns, or to get random samples from each table. Sending a query is done via the `execute, execute_all` methods, provided by `pymysql`. They provide a guarantee to preprocess the string to prevent SQL injections. Each one also includes randomization, as to ensure that the data will not be biased towards alphanumerical ordering preference.

#### <span>load_from_osm.py</span>

I created several methods for extracting different types of features from the OpenStreetMap API, combined by counting, existence or distance metrics. This module serves to provide a bridge between the 'Access' and 'Assess' part of the pipeline, as it provides simplified access to OSM, but also does some preprocessing, such as computing distances or matching buildings to their counterparts.

#### <span>assess.py</span>

Contains the core methods for evaluating metrics. This includes a method to remove outliers, dimensionality reduction via PCA, and feature transformation via One-Hot Encoding.

#### <span>address.py</span>

This module is used to evaluate the features, using an OLS model. It performs k-fold cross validation, and can get an average value for the loss function, provided to it, which is used for validation.

## Version Control

I used Git and GitHub for version control. The commit history should be publicly available <a href ="https://github.com/1414vo/adslib/commits/master">here</a>. Everything was done in the 'master' branch, as there was no purpose to branch out when I was the only one making changes, and there was no one to verify the pull requests. Most commits are well documented, but there was an issue with my Anaconda virtual environment, which meant that I needed to update the version of the package each time I reinstalled for the changes to hold. That is why there are multiple separate commits for changing the version. 