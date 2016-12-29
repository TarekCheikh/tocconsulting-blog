// This binary is used to upload files to the given aws s3 bucket
package main

import (
	"fmt"
	"os"
	"path"
	"path/filepath"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3"
)

var preserveDirStructureBool bool

func main() {
	if len(os.Args) != 6 {
		fmt.Println("Usage : ", os.Args[0],
			" aws_profile_name bucket_name bucket_prefix"+
				" file|directory preserveDirStructure'yes|no'")
		os.Exit(1)
	}
	// Check that we send the correct string for "preserveDirStructure"
	if os.Args[5] != "yes" && os.Args[5] != "no" {
		fmt.Println("preserveDirStructure accepts only 'yes' or 'no'")
		os.Exit(1)
	}
	if os.Args[5] == "yes" {
		preserveDirStructureBool = true
	} else {
		preserveDirStructureBool = false
	}
	// Make an aws session
	sess := makeSession(os.Args[1])
	if isDirectory(os.Args[4]) {
		uploadDirToS3(sess, os.Args[2], os.Args[3], os.Args[4])
	} else {
		uploadFileToS3(sess, os.Args[2], os.Args[3], os.Args[4])
	}
}

func isDirectory(path string) bool {
	fd, err := os.Stat(path)
	if err != nil {
		fmt.Println(err)
		os.Exit(2)
	}
	switch mode := fd.Mode(); {
	case mode.IsDir():
		return true
	case mode.IsRegular():
		return false
	}
	return false
}

func uploadDirToS3(sess *session.Session, bucketName string, bucketPrefix string, dirPath string) {
	fileList := []string{}
	filepath.Walk(dirPath, func(path string, f os.FileInfo, err error) error {
		fmt.Println("PATH ==> " + path)
		if isDirectory(path) {
			// Do nothing
			return nil
		} else {
			fileList = append(fileList, path)
			return nil
		}
	})

	for _, file := range fileList {
		uploadFileToS3(sess, bucketName, bucketPrefix, file)
	}
}

func uploadFileToS3(sess *session.Session, bucketName string, bucketPrefix string, filePath string) {
	fmt.Println("upload " + filePath + " to S3")
	// An s3 service
	s3Svc := s3.New(sess)
	file, err := os.Open(filePath)
	if err != nil {
		fmt.Println("Failed to open file", file, err)
		os.Exit(1)
	}
	defer file.Close()
	var key string
	if preserveDirStructureBool {
		fileDirectory, _ := filepath.Abs(filePath)
		key = bucketPrefix + fileDirectory
	} else {
		key = bucketPrefix + path.Base(filePath)
	}
	// Upload the file to the s3 given bucket
	params := &s3.PutObjectInput{
		Bucket: aws.String(bucketName), // Required
		Key:    aws.String(key),        // Required
		Body:   file,
	}
	_, err = s3Svc.PutObject(params)
	if err != nil {
		fmt.Printf("Failed to upload data to %s/%s, %s\n",
			bucketName, key, err.Error())
		return
	}
}

func makeSession(profile string) *session.Session {
	// Enable loading shared config file
	os.Setenv("AWS_SDK_LOAD_CONFIG", "1")
	// Specify profile to load for the session's config
	sess, err := session.NewSessionWithOptions(session.Options{
		Profile: profile,
	})
	if err != nil {
		fmt.Println("failed to create session,", err)
		fmt.Println(err)
		os.Exit(1)
	}

	return sess
}
