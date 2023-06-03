use polars::io::{csv::CsvReader, SerReader};
use polars::prelude::*;
use std::fs::File;

#[test]
fn test_df() {
    let df =
        CsvReader::from_path("../Trials/GR13-1208 (OLD) (LEFT) (S) (1)/computation_parameters.csv")
            .expect("Failed to find the csv file")
            .has_header(true)
            .finish()
            .expect("Failed to bring in the df");
    // for (j, column) in df.iter().enumerate() {
    //     for (i, element) in column.iter().enumerate() {
    //         println!("\nPosition: ({}, {}) \nValue: {}", i, j, element);
    //     }
    // }
    println!("{:?}", df.get(1).unwrap());
    assert!(true);
}
