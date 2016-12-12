// Get all files from the given s3 bucket
package main

import (
	"fmt"
	"io"
	"log"
	"os"
	"strings"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
)

// To hold the number retrieved files
var numberOfRetrievedFiles = 0

func main() {
	if len(os.Args) != 4 {
		fmt.Println("Usage : ", os.Args[0],
			" aws_profile_name s3bucket destDirPath")
		os.Exit(1)
	}
	fmt.Println("Getting all files from the s3 bucket :", os.Args[2])
	fmt.Println("And will download them to :", os.Args[3])
	sess := makeSession(os.Args[1])
	getBucketObjects(sess)
	// Print number of retrieved files
	fmt.Printf("We got %d files from our s3 bucket\n",
		numberOfRetrievedFiles)
}

func makeSession(profile string) *session.Session {
	// Enable loading shared config file
	os.Setenv("AWS_SDK_LOAD_CONFIG", "1")
	// Specify profile to load for the session's config
	sess, err := session.NewSessionWithOptions(session.Options{
		Config:  aws.Config{Region: aws.String("eu-west-1")},
		Profile: profile,
	})
	if err != nil {
		fmt.Println("failed to create session,", err)
		fmt.Println(err)
		os.Exit(2)
	}

	return sess
}

func getBucketObjects(sess *session.Session) {
	query := &s3.ListObjectsV2Input{
		Bucket: aws.String(os.Args[2]),
	}
	svc := s3.New(sess)

	// Flag used to check if we need to go further
	truncatedListing := true

	for truncatedListing {
		resp, err := svc.ListObjectsV2(query)

		if err != nil {
			// Print the error.
			fmt.Println(err.Error())
			return
		}
		// Get all files
		getObjectsAll(resp, svc)
		// Set continuation token
		query.ContinuationToken = resp.NextContinuationToken
		truncatedListing = *resp.IsTruncated
	}
}

func getObjectsAll(bucketObjectsList *s3.ListObjectsV2Output, s3Client *s3.S3) {
	//fmt.Println("One ring to rule them all")
	// Iterate through the files inside the bucket
	for _, key := range bucketObjectsList.Contents {
		destFilename := *key.Key
		if strings.HasSuffix(*key.Key, "/") {
			fmt.Println("Got a directory")
			continue
		}
		numberOfRetrievedFiles++
		if strings.Contains(*key.Key, "/") {
			var dirTree string
			// split
			s3FileFullPathList := strings.Split(*key.Key, "/")
			fmt.Println(s3FileFullPathList)
			fmt.Println("destFilename " + destFilename)
			for _, dir := range s3FileFullPathList[:len(s3FileFullPathList)-1] {
				dirTree += "/" + dir
			}
			os.MkdirAll(os.Args[3]+"/"+dirTree, 0775)
		}
		out, err := s3Client.GetObject(&s3.GetObjectInput{
			Bucket: aws.String(os.Args[2]),
			Key:    key.Key,
		})
		if err != nil {
			log.Fatal(err)
		}
		destFilePath := os.Args[3] + destFilename
		destFile, err := os.Create(destFilePath)
		if err != nil {
			log.Fatal(err)
		}
		bytes, err := io.Copy(destFile, out.Body)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("File %s contanin %d bytes\n", destFilePath, bytes)
		out.Body.Close()
		destFile.Close()
	}
}
