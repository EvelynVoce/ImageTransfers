How to run frontend

cd into frontend/my-uploader
npm install 
npm run start

How to run backend
cd into backend
uvicorn main:app --reload


Here you see a version which saves files to disk before being uploaded to a database

Another solution would be to:
1) refactor check exists to check the database has no images for that given serial 
2) upload each batch to DB one at a time
3) refactor check_uploads to perform a count on images in the DB for a given serial 
3.1) If upload has incorrect count, remove all images from DB OR set an invalidated flag on them

This would impose a risk that if an upload was mid way through and another user tried to query those images they could get a response with missing data
To avoid this the frontend should also perform a count on data returned
